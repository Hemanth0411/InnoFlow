from django.contrib import admin
from .models import AIModelConfig, ModelComparison, ModelResponse, TaskStatus

admin.site.register(AIModelConfig)
admin.site.register(ModelComparison)
admin.site.register(ModelResponse)
admin.site.register(TaskStatus)