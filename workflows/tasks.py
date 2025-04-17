# workflows/tasks.py
from celery import shared_task
from .models import Workflow, WorkflowExecution
import logging
import asyncio

logger = logging.getLogger(__name__)

from .execution import WorkflowExecutor

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def run_workflow(self, workflow_id, execution_id):
    try:
        workflow = Workflow.objects.get(id=workflow_id)
        execution = WorkflowExecution.objects.get(id=execution_id)
        
        # Initialize the WorkflowExecutor
        executor = WorkflowExecutor(execution)
        
        # Run the workflow using asyncio
        asyncio.run(executor.execute_workflow())
        
    except Workflow.DoesNotExist:
        logger.error(f"Workflow {workflow_id} not found")
        return {"error": "Workflow not found"}
    except WorkflowExecution.DoesNotExist:
        logger.error(f"WorkflowExecution {execution_id} not found")
        return {"error": "WorkflowExecution not found"}
    except Exception as e:
        logger.critical(f"Critical workflow error: {str(e)}", exc_info=True)
        raise self.retry(exc=e)