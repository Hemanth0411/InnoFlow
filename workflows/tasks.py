# workflows/tasks.py
from celery import shared_task
from .models import Workflow, WorkflowExecution
from .utils import execute_node
import logging
import json
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def run_workflow(self, workflow_id, execution_id):
    try:
        workflow = Workflow.objects.get(id=workflow_id)
        execution = WorkflowExecution.objects.get(id=execution_id)
        execution.status = 'running'
        execution.started_at = timezone.now()
        execution.save()

        nodes = workflow.nodes.all().order_by('order')
        results = []
        errors = []

        logger.info(f"Starting workflow {workflow_id} (execution {execution_id}) with {len(nodes)} nodes")

        for node in nodes:
            try:
                previous_output = results[-1] if results else None
                result = execute_node(node, previous_output)
                results.append({
                    'node_id': node.id,
                    'success': True,
                    'result': result
                })
            except Exception as e:
                logger.error(f"Execution {execution_id} failed at node {node.id}")
                errors.append({
                    'node_id': node.id,
                    'error': str(e),
                    'traceback': self.request.chain.traceback if self.request.chain else None
                })
                if not workflow.config.get('continue_on_error', False):
                    raise
                results.append({
                    'node_id': node.id,
                    'success': False,
                    'error': str(e)
                })

        execution.status = 'completed' if len(errors) == 0 else 'failed'
        execution.completed_at = timezone.now()
        execution.results = results
        execution.error_logs = json.dumps(errors)
        execution.save()

        return {
            'workflow_id': workflow_id,
            'execution_id': execution.id,
            'success': len(errors) == 0,
            'results': results,
            'errors': errors,
            'completed_nodes': len(nodes)
        }
    except Workflow.DoesNotExist:
        logger.error(f"Workflow {workflow_id} not found")
        return {"error": "Workflow not found"}
    except WorkflowExecution.DoesNotExist:
        logger.error(f"WorkflowExecution {execution_id} not found")
        return {"error": "WorkflowExecution not found"}
    except Exception as e:
        logger.critical(f"Critical workflow error: {str(e)}", exc_info=True)
        raise self.retry(exc=e)