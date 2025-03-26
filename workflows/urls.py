# workflows/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowViewSet, NodeViewSet, WorkflowExecutionViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin


router = DefaultRouter()
router.register(r'workflows', WorkflowViewSet)
router.register(r'nodes', NodeViewSet)
router.register(r'workflow_executions', WorkflowExecutionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('workflows.urls')),
]