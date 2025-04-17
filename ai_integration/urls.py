from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIModelConfigViewSet,
    ModelComparisonViewSet,
    TaskStatusViewSet
)

router = DefaultRouter()
router.register(r'aimodelconfig', AIModelConfigViewSet, basename='aimodelconfig')
router.register(r'modelcomparison', ModelComparisonViewSet, basename='modelcomparison')
router.register(r'taskstatus', TaskStatusViewSet, basename='taskview')

urlpatterns = [
    path('', include(router.urls)),
]