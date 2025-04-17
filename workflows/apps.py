from django.apps import AppConfig

class WorkflowsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workflows'

    def ready(self):
        from .mock_handlers import HANDLERS
        from .execution import NodeRegistry
        
        # Register handlers
        for node_type, handler in HANDLERS.items():
            NodeRegistry.register_handler(node_type, handler())