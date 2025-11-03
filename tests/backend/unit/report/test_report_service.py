"""
Unit tests for report service.
Tests PDF and Excel report generation with mock data.
"""
import pytest
from io import BytesIO
from types import SimpleNamespace

from backend.src.services import report as report_service
from tests.mock_data.report_data import (
    MOCK_PROJECT,
    MOCK_PROJECT_MINIMAL,
    INVALID_PROJECT_EMPTY,
    INVALID_PROJECT_NO_NAME,
    MOCK_TASKS_ALL_STATUSES,
    MOCK_TASKS_EMPTY,
    MOCK_TASKS_WITH_NULLS,
    MOCK_TASK_ASSIGNEES,
    MOCK_TASK_ASSIGNEES_EMPTY,
    MOCK_TASK_ASSIGNEES_ALL_UNASSIGNED,
    MOCK_TASK_LONG_TITLE,
    MOCK_TASK_NO_DATES
)

pytestmark = pytest.mark.unit


def dict_to_object(data: dict):
    return SimpleNamespace(**data)


def dicts_to_objects(task_dicts: list):
    return [dict_to_object(task) for task in task_dicts]


class TestGeneratePDFReport:

    def test_generate_pdf_report_success_with_all_statuses(self):
        pdf_buffer = report_service.generate_pdf_report(MOCK_PROJECT, dicts_to_objects(MOCK_TASKS_ALL_STATUSES), MOCK_TASK_ASSIGNEES)

        assert pdf_buffer is not None
        assert isinstance(pdf_buffer, BytesIO)

        pdf_buffer.seek(0)
        content = pdf_buffer.read()
        assert len(content) > 0
        assert content.startswith(b'%PDF')

    def test_generate_pdf_report_success_empty_tasks(self):
        pdf_buffer = report_service.generate_pdf_report(MOCK_PROJECT, dicts_to_objects(MOCK_TASKS_EMPTY), MOCK_TASK_ASSIGNEES_EMPTY)

        assert pdf_buffer is not None
        assert isinstance(pdf_buffer, BytesIO)

        pdf_buffer.seek(0)
        content = pdf_buffer.read()
        assert len(content) > 0
        assert content.startswith(b'%PDF')

    def test_generate_pdf_report_with_null_dates(self):
        pdf_buffer = report_service.generate_pdf_report(MOCK_PROJECT, dicts_to_objects(MOCK_TASKS_WITH_NULLS), MOCK_TASK_ASSIGNEES)

        assert pdf_buffer is not None
        pdf_buffer.seek(0)
        content = pdf_buffer.read()
        assert len(content) > 0
        assert content.startswith(b'%PDF')

    def test_generate_pdf_report_with_long_title(self):
        tasks = [dict_to_object(MOCK_TASK_LONG_TITLE)]
        assignees = {6: ["Assignee"]}
        pdf_buffer = report_service.generate_pdf_report(MOCK_PROJECT, tasks, assignees)

        assert pdf_buffer is not None
        pdf_buffer.seek(0)
        content = pdf_buffer.read()
        assert len(content) > 0
        assert content.startswith(b'%PDF')

    def test_generate_pdf_report_all_unassigned(self):
        pdf_buffer = report_service.generate_pdf_report(MOCK_PROJECT, dicts_to_objects(MOCK_TASKS_ALL_STATUSES), MOCK_TASK_ASSIGNEES_ALL_UNASSIGNED)

        assert pdf_buffer is not None
        pdf_buffer.seek(0)
        content = pdf_buffer.read()
        assert len(content) > 0
        assert content.startswith(b'%PDF')

    def test_generate_pdf_report_minimal_project(self):
        pdf_buffer = report_service.generate_pdf_report(MOCK_PROJECT_MINIMAL, dicts_to_objects(MOCK_TASKS_ALL_STATUSES), MOCK_TASK_ASSIGNEES)

        assert pdf_buffer is not None
        pdf_buffer.seek(0)
        content = pdf_buffer.read()
        assert len(content) > 0
        assert content.startswith(b'%PDF')

    def test_generate_pdf_report_empty_project_raises_error(self):
        with pytest.raises(ValueError, match="Project data is required"):
            report_service.generate_pdf_report(INVALID_PROJECT_EMPTY, dicts_to_objects(MOCK_TASKS_ALL_STATUSES), MOCK_TASK_ASSIGNEES)

    def test_generate_pdf_report_no_project_name_raises_error(self):
        with pytest.raises(ValueError, match="Project name is required"):
            report_service.generate_pdf_report(INVALID_PROJECT_NO_NAME, dicts_to_objects(MOCK_TASKS_ALL_STATUSES), MOCK_TASK_ASSIGNEES)


class TestGenerateExcelReport:
    def test_generate_excel_report_success_with_all_statuses(self):
        excel_buffer = report_service.generate_excel_report(MOCK_PROJECT, dicts_to_objects(MOCK_TASKS_ALL_STATUSES), MOCK_TASK_ASSIGNEES)

        assert excel_buffer is not None
        assert isinstance(excel_buffer, BytesIO)
        excel_buffer.seek(0)
        content = excel_buffer.read()
        assert len(content) > 0
        assert content.startswith(b'PK')

    def test_generate_excel_report_success_empty_tasks(self):
        excel_buffer = report_service.generate_excel_report(MOCK_PROJECT, dicts_to_objects(MOCK_TASKS_EMPTY), MOCK_TASK_ASSIGNEES_EMPTY)

        assert excel_buffer is not None
        assert isinstance(excel_buffer, BytesIO)

        excel_buffer.seek(0)
        content = excel_buffer.read()
        assert len(content) > 0
        assert content.startswith(b'PK')

    def test_generate_excel_report_with_null_dates(self):
        excel_buffer = report_service.generate_excel_report(MOCK_PROJECT, dicts_to_objects(MOCK_TASKS_WITH_NULLS), MOCK_TASK_ASSIGNEES)

        assert excel_buffer is not None
        excel_buffer.seek(0)
        content = excel_buffer.read()
        assert len(content) > 0
        assert content.startswith(b'PK')

    def test_generate_excel_report_validates_content(self):
        from openpyxl import load_workbook

        excel_buffer = report_service.generate_excel_report(MOCK_PROJECT, dicts_to_objects(MOCK_TASKS_ALL_STATUSES), MOCK_TASK_ASSIGNEES)

        excel_buffer.seek(0)
        wb = load_workbook(excel_buffer)

        assert "Project Schedule Report" in wb.sheetnames

        ws = wb["Project Schedule Report"]

        assert ws["A1"].value is not None
        assert "Project Schedule Report" in str(ws["A1"].value)

        assert ws["A2"].value == "Project Name"
        assert ws["B2"].value == MOCK_PROJECT["project_name"]

        assert ws["A4"].value == "Summary"
        assert ws["A5"].value == "Metric"
        assert ws["B5"].value == "Count"

    def test_generate_excel_report_all_unassigned(self):
        excel_buffer = report_service.generate_excel_report(MOCK_PROJECT, dicts_to_objects(MOCK_TASKS_ALL_STATUSES), MOCK_TASK_ASSIGNEES_ALL_UNASSIGNED)

        assert excel_buffer is not None
        excel_buffer.seek(0)
        content = excel_buffer.read()
        assert len(content) > 0
        assert content.startswith(b'PK')

    def test_generate_excel_report_minimal_project(self):
        excel_buffer = report_service.generate_excel_report(MOCK_PROJECT_MINIMAL, dicts_to_objects(MOCK_TASKS_ALL_STATUSES), MOCK_TASK_ASSIGNEES)

        assert excel_buffer is not None
        excel_buffer.seek(0)
        content = excel_buffer.read()
        assert len(content) > 0
        assert content.startswith(b'PK')

    def test_generate_excel_report_empty_project_raises_error(self):
        with pytest.raises(ValueError, match="Project data is required"):
            report_service.generate_excel_report(INVALID_PROJECT_EMPTY, dicts_to_objects(MOCK_TASKS_ALL_STATUSES), MOCK_TASK_ASSIGNEES)

    def test_generate_excel_report_no_project_name_raises_error(self):
        with pytest.raises(ValueError, match="Project name is required"):
            report_service.generate_excel_report(INVALID_PROJECT_NO_NAME, dicts_to_objects(MOCK_TASKS_ALL_STATUSES), MOCK_TASK_ASSIGNEES)


    def test_generate_excel_report_task_summary_counts(self):
        from openpyxl import load_workbook

        excel_buffer = report_service.generate_excel_report(MOCK_PROJECT, dicts_to_objects(MOCK_TASKS_ALL_STATUSES), MOCK_TASK_ASSIGNEES)
        excel_buffer.seek(0)
        wb = load_workbook(excel_buffer)
        ws = wb["Project Schedule Report"]

        summary_dict = {}
        for row in range(6, 12):
            metric = ws[f"A{row}"].value
            count = ws[f"B{row}"].value
            if metric and count is not None:
                summary_dict[metric] = count
        assert summary_dict.get("Total Tasks") == len(MOCK_TASKS_ALL_STATUSES)
        assert summary_dict.get("Projected Tasks") == 1
        assert summary_dict.get("In-Progress Tasks") == 1
        assert summary_dict.get("Completed Tasks") == 1 
        assert summary_dict.get("Under Review Tasks") == 1

    def test_generate_excel_report_column_width(self):
        from openpyxl import load_workbook
        excel_buffer = report_service.generate_excel_report(MOCK_PROJECT, dicts_to_objects(MOCK_TASKS_ALL_STATUSES), MOCK_TASK_ASSIGNEES)
        excel_buffer.seek(0)
        wb = load_workbook(excel_buffer)
        ws = wb["Project Schedule Report"]
        for col_letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            col_width = ws.column_dimensions[col_letter].width
            assert col_width >= 10, f"Column {col_letter} should have minimum width"
            assert col_width <= 50, f"Column {col_letter} should have maximum width"

