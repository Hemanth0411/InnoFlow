from django.urls import re_path
from workflows.consumers import WorkflowExecutionConsumer

websocket_urlpatterns = [
    re_path(r'ws/workflow-executions/(?P<execution_id>[\w-]+)/$', WorkflowExecutionConsumer.as_asgi()),
]