from django.shortcuts import render
from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from .models import Workflow, Node, WorkflowExecution
from .serializers import WorkflowSerializer, NodeSerializer, WorkflowExecutionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from .tasks import run_workflow
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

class WorkflowViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing workflows.
    
    list:
    Return a list of all workflows owned by the current user.
    
    create:
    Create a new workflow.
    
    retrieve:
    Return a specific workflow by ID.
    
    update:
    Update a workflow.
    
    partial_update:
    Partially update a workflow.
    
    destroy:
    Delete a workflow.
    """
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated]
    queryset = Workflow.objects.all()

    def get_queryset(self):
        """Return only workflows owned by the current user."""
        return Workflow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new workflow with the current user as owner."""
        serializer.save(user=self.request.user)


    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        try:
            workflow = self.get_object()
            execution = WorkflowExecution.objects.create(
                workflow=workflow,
                status='pending'
            )
            run_workflow.delay(workflow.id, execution.id)
            return Response({
                "status": "Workflow execution started",
                "execution_id": execution.id,
                "websocket_url": f"/ws/workflow-executions/{execution.id}/"
            })
        except Exception as e:
            return Response({
                "error": str(e),
                "message": "Failed to start workflow execution"
            }, status=400)

    
class NodeViewSet(viewsets.ModelViewSet):
    serializer_class = NodeSerializer
    permission_classes = [IsAuthenticated]
    queryset = Node.objects.all()

    def get_queryset(self):
        user_workflows = Workflow.objects.filter(user=self.request.user)
        return Node.objects.filter(workflow__in=user_workflows)

    def perform_create(self, serializer):
        workflow = serializer.validated_data['workflow']
        if workflow.user != self.request.user:
            raise serializers.ValidationError("Cannot create nodes for a workflow you do not own.")
        serializer.save()


class WorkflowExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WorkflowExecution.objects.all()
    serializer_class = WorkflowExecutionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_workflows = Workflow.objects.filter(user=self.request.user)
        return self.queryset.filter(workflow__in=user_workflows)