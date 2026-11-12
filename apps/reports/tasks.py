import logging
from django.utils import timezone
from config.celery import app
from apps.reports.models import ReportJob
from engine.templates.parser import TemplateCompiler
from engine.storage.manager import get_storage

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3)
def generate_report_async_task(self, report_id: str, payload_dict: dict):
    """
    Celery asynchronous task for executing document composition and rendering.
    """
    try:
        report = ReportJob.objects.get(id=report_id)
        report.status = ReportJob.STATUS_PROCESSING
        report.save(update_fields=["status"])

        compiler = TemplateCompiler()
        doc = compiler.compile(payload_dict)
        pdf_bytes = doc.render()

        storage = get_storage()
        storage_key = f"reports/{report.application.id}/{report.id}.pdf"
        storage.save(storage_key, pdf_bytes, content_type="application/pdf")

        report.status = ReportJob.STATUS_COMPLETED
        report.storage_key = storage_key
        report.file_size = len(pdf_bytes)
        report.completed_at = timezone.now()
        report.save()

        logger.info(f"Report {report_id} successfully generated.")
        return {"report_id": report_id, "status": "completed", "size": len(pdf_bytes)}

    except Exception as exc:
        logger.error(f"Error generating report {report_id}: {exc}", exc_info=True)
        try:
            report = ReportJob.objects.get(id=report_id)
            report.status = ReportJob.STATUS_FAILED
            report.error_message = str(exc)
            report.save(update_fields=["status", "error_message"])
        except Exception:
            pass
        raise exc
