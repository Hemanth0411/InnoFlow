from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()

class Workflow(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    config = models.JSONField(default=dict)

    def __str__(self):
        return self.name

class Node(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='nodes')
    type = models.CharField(max_length=50)
    config = models.JSONField(default=dict)
    order = models.IntegerField()
    is_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.type} (Workflow: {self.workflow.name})'

class WorkflowExecution(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='executions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    results = models.JSONField(null=True, blank=True)
    error_logs = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Execution of {self.workflow.name} ({self.status.capitalize()})"

class NodeConnection(models.Model):
    source_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='outgoing_connections')
    target_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='incoming_connections')
    source_port = models.CharField(max_length=50, default='output')
    target_port = models.CharField(max_length=50, default='input')

    