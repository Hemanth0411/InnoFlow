# workflows/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowViewSet, NodeViewSet, WorkflowExecutionViewSet

router = DefaultRouter()
router.register(r'workflows', WorkflowViewSet)
router.register(r'nodes', NodeViewSet)
router.register(r'workflow_executions', WorkflowExecutionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]