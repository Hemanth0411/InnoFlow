from celery import shared_task
from django.utils import timezone
from .models import WorkflowExecution, Node, NodeConnection
from workflows.utils import execute_node  # Import the execute_node function
from typing import Any, Dict

class WorkflowExecutor:
    def __init__(self, execution: WorkflowExecution):
        self.execution = execution
        self.context = {}
        self.results = {}

    def execute_node(self, node: Node, input_data: Any = None) -> Dict:
        try:
            result = execute_node(node, input_data, continue_on_error=False)
            self.results[node.id] = result
            return result
        except Exception as e:
            if node.retry_count < node.max_retries:
                node.retry_count += 1
                node.save()
                return self.execute_node(node, input_data)
            raise

    def execute_workflow(self):
        try:
            self.execution.status = 'running'
            self.execution.started_at = timezone.now()
            self.execution.save()

            nodes = Node.objects.filter(
                workflow=self.execution.workflow,
                is_enabled=True
            ).order_by('order')

            for node in nodes:
                input_data = self.get_node_input(node)
                result = self.execute_node(node, input_data)

            self.execution.status = 'completed'
            self.execution.completed_at = timezone.now()
            self.execution.results = self.results
            self.execution.save()
        except Exception as e:
            self.execution.status = 'failed'
            self.execution.error_logs = str(e)
            self.execution.save()
            raise

    def get_node_input(self, node: Node) -> Any:
        input_connections = NodeConnection.objects.filter(
            target_node=node,
            target_port='input'
        )
        if not input_connections:
            return None
        source_connection = input_connections.first()
        source_result = self.results.get(source_connection.source_node_id)
        return source_result
