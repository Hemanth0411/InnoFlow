from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

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
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='nodes')  # Link to workflow
    type = models.CharField(max_length=50)  # Type of node (e.g., "text_input", "openai_tts")
    config = models.JSONField(default=dict)  # Configuration for the node (e.g., AI model settings)
    order = models.IntegerField()  # Order of execution (1, 2, 3...)

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

    def __str__(self):
        return f"Execution {self.id} of {self.workflow.name}"