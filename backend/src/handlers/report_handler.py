"""
Report handler for project schedule reports.
"""
from __future__ import annotations

import logging
from io import BytesIO

from backend.src.services import report as report_service
from backend.src.services import project as project_service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def generate_pdf_report(project_id: int) -> BytesIO:
    """
    Generate a PDF report for a project.
    Returns BytesIO buffer with PDF content.
    """
    # Validate project exists
    project = project_service.get_project_by_id(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")
    
    logger.info(f"Generating PDF report for project {project_id}")
    
    try:
        pdf_buffer = report_service.generate_pdf_report(project_id)
        logger.info(f"Successfully generated PDF report for project {project_id}")
        return pdf_buffer
    except Exception as e:
        logger.error(f"Error generating PDF report for project {project_id}: {str(e)}")
        raise


def generate_excel_report(project_id: int) -> BytesIO:
    """
    Generate an Excel report for a project.
    Returns BytesIO buffer with Excel content.
    """
    # Validate project exists
    project = project_service.get_project_by_id(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")
    
    logger.info(f"Generating Excel report for project {project_id}")
    
    try:
        excel_buffer = report_service.generate_excel_report(project_id)
        logger.info(f"Successfully generated Excel report for project {project_id}")
        return excel_buffer
    except Exception as e:
        logger.error(f"Error generating Excel report for project {project_id}: {str(e)}")
        raise

