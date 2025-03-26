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
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workflow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        workflow = self.get_object()
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            status='pending'
        )
        run_workflow.delay(workflow.id, execution.id)
        return Response({
            "status": "Workflow execution started",
            "execution_id": execution.id
        })

class NodeViewSet(viewsets.ModelViewSet):
    serializer_class = NodeSerializer
    permission_classes = [IsAuthenticated]

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