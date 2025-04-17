from typing import List, Dict
from .models import Workflow, Node, NodePort, NodeConnection, WorkflowExecution

class WorkflowValidator:
    @staticmethod
    def validate_workflow(workflow: Workflow) -> List[str]:
        errors = []
        
        # Validate workflow structure
        if not workflow.nodes.exists():
            errors.append("Workflow has no nodes")
            return errors

        # Validate node connections
        for node in workflow.nodes.all():
            required_inputs = NodePort.objects.filter(
                node=node,
                is_input=True,
                is_required=True
            )
            
            for port in required_inputs:
                if not NodeConnection.objects.filter(
                    target_node=node,
                    target_port=port
                ).exists():
                    errors.append(f"Required input '{port.name}' not connected for node {node.name}")

        # Validate execution order
        orders = list(workflow.nodes.values_list('order', flat=True))
        if len(set(orders)) != len(orders):
            errors.append("Duplicate node execution orders found")

        # New: Validate node types
        valid_node_types = ["text_input", "openai_tts", "huggingface_summarization"]
        for node in workflow.nodes.all():
            if node.type not in valid_node_types:
                errors.append(f"Invalid node type: {node.type}")

        # New: Validate node configurations
        for node in workflow.nodes.all():
            if node.type == "openai_tts" and 'voice' not in node.config:
                errors.append(f"Missing 'voice' in config for node {node.name}")

        return errors