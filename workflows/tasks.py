from celery import shared_task
from .models import Workflow, WorkflowExecution
from .execution import WorkflowExecutor
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def run_workflow(self, workflow_id, execution_id):
    try:
        workflow = Workflow.objects.get(id=workflow_id)
        execution = WorkflowExecution.objects.get(id=execution_id)
        executor = WorkflowExecutor(execution)
        executor.execute_workflow()
    except Workflow.DoesNotExist:
        logger.error(f"Workflow {workflow_id} not found")
    except WorkflowExecution.DoesNotExist:
        logger.error(f"WorkflowExecution {execution_id} not found")
    except Exception as e:
        logger.critical(f"Critical workflow error: {str(e)}", exc_info=True)
        raise self.retry(exc=e)