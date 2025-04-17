from celery import shared_task
from django.utils import timezone
from .models import WorkflowExecution, Node, NodeConnection, NodePort
import asyncio
from typing import Dict, Any
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging
import traceback

logger = logging.getLogger(__name__)

class NodeRegistry:
    _handlers = {}

    @classmethod
    def register_handler(cls, node_type: str, handler):
        cls._handlers[node_type] = handler

    @classmethod
    def get_handler(cls, node_type: str):
        return cls._handlers.get(node_type)

class WorkflowExecutor:
    def __init__(self, execution: WorkflowExecution):
        self.execution = execution
        self.context = {}
        self.results = {}
        self.channel_layer = get_channel_layer()

    async def execute_node(self, node: Node, input_data: Any = None) -> Dict:
        try:
            # Get node handler from registry
            handler = NodeRegistry.get_handler(node.type)
            if not handler:
                raise ValueError(f"No handler found for node type: {node.type}")

            # Execute node with timeout
            async with asyncio.timeout(node.timeout):
                result = await handler.execute(node, input_data, self.context)
                
            # Store result
            self.results[node.id] = result

            # Send success update
            async_to_sync(self.channel_layer.group_send)(
                f'execution_{self.execution.id}',
                {
                    'type': 'send_update',
                    'message': f'Node {node.name} executed successfully',
                    'status': 'progress',
                    'results': {node.id: result},
                }
            )

            return result

        except asyncio.TimeoutError:
            logger.error(
            f"Node {node.id} execution timed out",
            extra={'node_id': node.id, 'workflow_id': self.execution.workflow.id}
        )
            raise
        except Exception as e:
            logger.error(
            f"Error executing node {node.id}: {str(e)}",
            exc_info=True,  # Include traceback
            extra={'node_id': node.id, 'workflow_id': self.execution.workflow.id}
        )
            if node.retry_count < node.max_retries:
                node.retry_count += 1
                node.save()
                return await self.execute_node(node, input_data)
            # Log error and send update after retries exhausted
            logger.error(
                f"Error executing node {node.id}: {str(e)}",
                exc_info=True,
                extra={'node_id': node.id, 'workflow_id': self.execution.workflow.id}
            )
            self.execution.error_logs = traceback.format_exc()
            self.execution.save()
            
            async_to_sync(self.channel_layer.group_send)(
                f'execution_{self.execution.id}',
                {
                    'type': 'send_update',
                    'message': f'Error executing node {node.name}',
                    'status': 'error',
                    'errors': {node.id: str(e)},
                }
            )
            raise

    async def execute_workflow(self):
        try:
            self.execution.status = 'running'
            self.execution.started_at = timezone.now()
            self.execution.save()

            # Send workflow start update
            async_to_sync(self.channel_layer.group_send)(
                f'execution_{self.execution.id}',
                {
                    'type': 'send_update',
                    'message': 'Workflow execution started',
                    'status': 'running',
                }
            )

            # Get nodes in execution order
            nodes = Node.objects.filter(
                workflow=self.execution.workflow,
                is_enabled=True
            ).order_by('order')

            for node in nodes:
                input_data = await self.get_node_input(node)
                result = await self.execute_node(node, input_data)

            self.execution.status = 'completed'
            self.execution.completed_at = timezone.now()
            self.execution.results = self.results
            self.execution.save()

            # Send workflow completion update
            async_to_sync(self.channel_layer.group_send)(
                f'execution_{self.execution.id}',
                {
                    'type': 'send_update',
                    'message': 'Workflow execution completed',
                    'status': 'completed',
                    'results': self.results,
                }
            )

        except Exception as e:
            logger.error(
                f"Workflow execution failed: {str(e)}",
                exc_info=True,
                extra={'workflow_id': self.execution.workflow.id}
            )
            self.execution.status = 'failed'
            self.execution.error_logs = traceback.format_exc()
            self.execution.save()
            
            # Send workflow failure update
            async_to_sync(self.channel_layer.group_send)(
                f'execution_{self.execution.id}',
                {
                    'type': 'send_update',
                    'message': 'Workflow execution failed',
                    'status': 'failed',
                    'errors': {'workflow': str(e)},
                }
            )
            raise

    async def get_node_input(self, node: Node) -> Any:
        # Existing implementation remains unchanged
        input_ports = NodePort.objects.filter(node=node, is_input=True)
        input_data = {}
        for port in input_ports:
            connections = NodeConnection.objects.filter(
                target_node=node, target_port=port
            )
            if connections.exists():
                connection = connections.first()
                source_node_id = connection.source_node_id
                source_port_name = connection.source_port.name
                if source_node_id in self.results:
                    input_data[port.name] = self.results[source_node_id].get(source_port_name)
                else:
                    input_data[port.name] = None
            else:
                if port.is_required:
                    raise ValueError(f"Required input port '{port.name}' for node {node.name} is not connected")
                input_data[port.name] = None
        return input_data
    

