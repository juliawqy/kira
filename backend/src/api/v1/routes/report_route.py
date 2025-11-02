"""
API routes for project report generation and export.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from io import BytesIO

import backend.src.handlers.report_handler as report_handler

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/project/{project_id}/pdf", name="export_pdf_report")
def export_pdf_report(project_id: int):
    """
    Export a project schedule report as PDF.
    Shows projected, in-progress, completed, and under review tasks.
    """
    try:
        pdf_buffer = report_handler.generate_pdf_report(project_id)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=project_{project_id}_schedule_report.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF report: {str(e)}")


@router.get("/project/{project_id}/excel", name="export_excel_report")
def export_excel_report(project_id: int):
    """
    Export a project schedule report as Excel.
    Shows projected, in-progress, completed, and under review tasks.
    """
    try:
        excel_buffer = report_handler.generate_excel_report(project_id)
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=project_{project_id}_schedule_report.xlsx"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Excel report: {str(e)}")

