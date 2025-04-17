from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json
import uuid


User = get_user_model()

class Workflow(models.Model):
    """
    Represents a workflow created by a user.
    """
    name = models.CharField(max_length=100)  # Name of the workflow
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who created the workflow
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Last updated timestamp
    config = models.JSONField(default=dict)
    def __str__(self):
        return self.name

class Node(models.Model):
    """
    Represents a step in a workflow.
    """
    name = models.CharField(max_length=100, default="")
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='nodes')
    type = models.CharField(max_length=50)
    config = models.JSONField(default=dict)
    order = models.IntegerField()
    retry_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']  # Default ordering by the 'order' field

    def __str__(self):
        return f"{self.type} (Order: {self.order})"

class WorkflowExecution(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    workflow = models.ForeignKey(
        'Workflow',
        on_delete=models.CASCADE,
        related_name='executions'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    results = models.JSONField(null=True, blank=True)
    error_logs = models.TextField(null=True, blank=True)
    execution_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    execution_context = models.JSONField(default=dict, blank=True, null=True)
    variables = models.JSONField(default=dict, blank=True, null=True)
    started_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Execution {self.id} of {self.workflow.name}"
    
class NodePort(models.Model):
    """
    Represents an input/output port on a node.
    """
    node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='ports')
    name = models.CharField(max_length=50)
    is_input = models.BooleanField(default=True)
    is_required = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Port {self.name} (Node: {self.node.name})"

class NodeConnection(models.Model):
    """
    Represents a connection between two ports on different nodes.
    """
    source_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='source_connections')
    source_port = models.ForeignKey(NodePort, on_delete=models.CASCADE, related_name='source_port')
    target_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='target_connections')
    target_port = models.ForeignKey(NodePort, on_delete=models.CASCADE, related_name='target_port')

    def __str__(self):
        return f"Connection: {self.source_node.name}.{self.source_port.name} -> {self.target_node.name}.{self.target_port.name}"