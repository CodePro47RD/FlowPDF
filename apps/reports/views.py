import io
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.templates.models import Template
from .models import ReportJob
from .serializers import (
    GenerateReportRequestSerializer,
    ReportJobResponseSerializer,
)
from .tasks import generate_report_async_task
from engine.templates.parser import TemplateCompiler
from engine.storage.manager import get_storage


class ReportGenerateView(APIView):
    """
    Generate a PDF document from a stored template or inline JSON definition.
    Supports synchronous binary streaming or asynchronous background worker execution.
    """

    @extend_schema(
        request=GenerateReportRequestSerializer,
        responses={
            200: OpenApiResponse(description="PDF binary stream (synchronous binary mode)"),
            201: ReportJobResponseSerializer,
            202: ReportJobResponseSerializer,
            400: OpenApiResponse(description="Validation or template syntax error"),
        },
        summary="Generate a document or report",
    )
    def post(self, request):
        serializer = GenerateReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        app = getattr(request, "application", None)

        # 1. Resolve document layout definition
        template_obj = None
        doc_definition = validated.get("document")

        if not doc_definition:
            tpl_identifier = validated.get("template")
            import uuid
            is_uuid = False
            try:
                uuid.UUID(str(tpl_identifier))
                is_uuid = True
            except (ValueError, TypeError, AttributeError):
                pass

            if app:
                if is_uuid:
                    template_obj = Template.objects.filter(application=app, id=tpl_identifier).first()
                if not template_obj:
                    template_obj = Template.objects.filter(application=app, name=tpl_identifier, is_active=True).first()
            else:
                if is_uuid:
                    template_obj = Template.objects.filter(id=tpl_identifier).first()

            if not template_obj:
                return Response(
                    {"error": f"Template '{tpl_identifier}' not found for this tenant."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            doc_definition = template_obj.definition

        # Prepare unified payload dict
        payload_dict = {
            "version": doc_definition.get("version", "1.0"),
            "document": doc_definition,
            "data": validated.get("data", {}),
        }

        # 2. Asynchronous Generation via Celery
        if validated.get("async_mode"):
            job = ReportJob.objects.create(
                application=app,
                template=template_obj,
                format=validated.get("format", "pdf"),
                status=ReportJob.STATUS_PENDING,
            )
            generate_report_async_task.delay(str(job.id), payload_dict)
            res_serializer = ReportJobResponseSerializer(job, context={"request": request})
            return Response(res_serializer.data, status=status.HTTP_202_ACCEPTED)

        # 3. Synchronous Generation
        compiler = TemplateCompiler()
        doc = compiler.compile(payload_dict)
        pdf_bytes = doc.render()

        # Direct binary stream response
        if validated.get("response_type") == "binary":
            response = HttpResponse(pdf_bytes, content_type="application/pdf")
            response["Content-Disposition"] = 'inline; filename="report.pdf"'
            return response

        # Save to storage and return JSON metadata
        job = ReportJob.objects.create(
            application=app,
            template=template_obj,
            format="pdf",
            status=ReportJob.STATUS_COMPLETED,
            file_size=len(pdf_bytes),
            completed_at=timezone.now(),
        )
        storage = get_storage()
        storage_key = f"reports/{app.id if app else 'public'}/{job.id}.pdf"
        storage.save(storage_key, pdf_bytes, content_type="application/pdf")
        job.storage_key = storage_key
        job.save(update_fields=["storage_key"])

        res_serializer = ReportJobResponseSerializer(job, context={"request": request})
        return Response(res_serializer.data, status=status.HTTP_201_CREATED)


class ReportPreviewView(APIView):
    """
    Instantly render and preview a document as a raw inline PDF binary.
    """

    @extend_schema(
        request=GenerateReportRequestSerializer,
        responses={200: OpenApiResponse(description="Inline PDF binary for browser rendering")},
        summary="Preview a document in real-time",
    )
    def post(self, request):
        serializer = GenerateReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        app = getattr(request, "application", None)
        doc_definition = validated.get("document")

        if not doc_definition:
            tpl_identifier = validated.get("template")
            import uuid
            is_uuid = False
            try:
                uuid.UUID(str(tpl_identifier))
                is_uuid = True
            except (ValueError, TypeError, AttributeError):
                pass

            if app:
                if is_uuid:
                    template_obj = Template.objects.filter(application=app, id=tpl_identifier).first()
                if not template_obj:
                    template_obj = Template.objects.filter(application=app, name=tpl_identifier, is_active=True).first()
            else:
                if is_uuid:
                    template_obj = Template.objects.filter(id=tpl_identifier).first()

            if not template_obj:
                return Response({"error": f"Template '{tpl_identifier}' not found"}, status=status.HTTP_404_NOT_FOUND)
            doc_definition = template_obj.definition

        payload_dict = {
            "version": doc_definition.get("version", "1.0"),
            "document": doc_definition,
            "data": validated.get("data", {}),
        }

        compiler = TemplateCompiler()
        doc = compiler.compile(payload_dict)
        pdf_bytes = doc.render()

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'inline; filename="preview.pdf"'
        return response


class ReportDetailView(APIView):
    """
    Check the processing status and metadata of a report generation job.
    """

    @extend_schema(
        responses={200: ReportJobResponseSerializer},
        summary="Get report job status and details",
    )
    def get(self, request, pk):
        app = getattr(request, "application", None)
        if app:
            job = get_object_or_404(ReportJob, id=pk, application=app)
        else:
            job = get_object_or_404(ReportJob, id=pk)

        serializer = ReportJobResponseSerializer(job, context={"request": request})
        return Response(serializer.data)


class ReportDownloadView(APIView):
    """
    Download the generated PDF document.
    """

    @extend_schema(
        responses={200: OpenApiResponse(description="PDF file binary attachment")},
        summary="Download completed PDF document",
    )
    def get(self, request, pk):
        app = getattr(request, "application", None)
        if app:
            job = get_object_or_404(ReportJob, id=pk, application=app)
        else:
            job = get_object_or_404(ReportJob, id=pk)

        if job.status != ReportJob.STATUS_COMPLETED or not job.storage_key:
            return Response(
                {"error": f"Report is not ready. Current status: '{job.status}'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        storage = get_storage()
        stream = storage.open(job.storage_key)
        return FileResponse(
            stream,
            content_type="application/pdf",
            as_attachment=True,
            filename=f"report_{job.id}.pdf",
        )
