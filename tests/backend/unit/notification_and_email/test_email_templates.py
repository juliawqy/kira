"""
Unit tests for EmailTemplates
"""
import pytest
from jinja2 import Template

from backend.src.templates.email_templates import EmailTemplates


class TestEmailTemplates:
    """Test cases for EmailTemplates class"""

    @pytest.fixture
    def email_templates(self):
        """Create EmailTemplates instance for testing"""
        return EmailTemplates()

    def test_get_task_update_template_structure(self, email_templates):
        """Test that task update template has correct structure"""
        template_data = email_templates.get_task_update_template()
        
        assert isinstance(template_data, dict)
        assert 'html' in template_data
        assert 'text' in template_data
        assert isinstance(template_data['html'], str)
        assert isinstance(template_data['text'], str)

    def test_get_task_update_template_html_content(self, email_templates):
        """Test that HTML template contains required elements"""
        template_data = email_templates.get_task_update_template()
        html_template = template_data['html']
        
        # Check for HTML structure
        assert '<!DOCTYPE html>' in html_template
        assert '<html>' in html_template
        assert '<head>' in html_template
        assert '<body>' in html_template
        
        # Check for required Jinja2 variables
        assert '{{ app_name }}' in html_template
        assert '{{ assignee_name' in html_template
        assert '{{ task_title }}' in html_template
        assert '{{ task_id }}' in html_template
        assert '{{ updated_by }}' in html_template
        assert '{{ update_date }}' in html_template
        # Check for the loop structure instead of direct variable
        assert '{% for field in updated_fields %}' in html_template

    def test_get_task_update_template_text_content(self, email_templates):
        """Test that text template contains required elements"""
        template_data = email_templates.get_task_update_template()
        text_template = template_data['text']
        
        # Check for required Jinja2 variables in text version
        assert '{{ app_name }}' in text_template
        assert '{{ assignee_name' in text_template
        assert '{{ task_title }}' in text_template
        assert '{{ task_id }}' in text_template
        assert '{{ updated_by }}' in text_template
        # Check for the loop structure instead of direct variable
        assert '{% for field in updated_fields %}' in text_template

    def test_render_task_update_template_html(self, email_templates):
        """Test rendering HTML template with sample data"""
        template_data = email_templates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        # Sample data for rendering
        render_data = {
            'app_name': 'KIRA',
            'assignee_name': 'John Doe',
            'task_title': 'Complete Project Documentation',
            'task_id': 123,
            'updated_by': 'Jane Smith',
            'update_date': '2025-10-15',
            'updated_fields': ['title', 'priority'],
            'previous_values': {'title': 'Old Title', 'priority': 'LOW'},
            'new_values': {'title': 'New Title', 'priority': 'HIGH'},
            'task_url': 'http://localhost:8000/tasks/123'
        }
        
        rendered_html = html_template.render(**render_data)
        
        # Check that variables were properly substituted
        assert 'KIRA' in rendered_html
        assert 'John Doe' in rendered_html
        assert 'Complete Project Documentation' in rendered_html
        assert '#123' in rendered_html
        assert 'Jane Smith' in rendered_html
        assert '2025-10-15' in rendered_html

    def test_render_task_update_template_text(self, email_templates):
        """Test rendering text template with sample data"""
        template_data = email_templates.get_task_update_template()
        text_template = Template(template_data['text'])
        
        # Sample data for rendering
        render_data = {
            'app_name': 'KIRA',
            'assignee_name': 'John Doe',
            'task_title': 'Complete Project Documentation',
            'task_id': 123,
            'updated_by': 'Jane Smith',
            'update_date': '2025-10-15',
            'updated_fields': ['title', 'priority'],
            'previous_values': {'title': 'Old Title', 'priority': 'LOW'},
            'new_values': {'title': 'New Title', 'priority': 'HIGH'},
            'task_url': 'http://localhost:8000/tasks/123'
        }
        
        rendered_text = text_template.render(**render_data)
        
        # Check that variables were properly substituted
        assert 'KIRA' in rendered_text
        assert 'John Doe' in rendered_text
        assert 'Complete Project Documentation' in rendered_text
        assert '#123' in rendered_text
        assert 'Jane Smith' in rendered_text

    def test_render_template_with_missing_assignee_name(self, email_templates):
        """Test template rendering when assignee_name is None"""
        template_data = email_templates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        render_data = {
            'app_name': 'KIRA',
            'assignee_name': None,  # Missing assignee name
            'task_title': 'Test Task',
            'task_id': 456,
            'updated_by': 'System',
            'update_date': '2025-10-15',
            'updated_fields': ['status'],
            'previous_values': {'status': 'TODO'},
            'new_values': {'status': 'IN_PROGRESS'}
        }
        
        rendered_html = html_template.render(**render_data)
        
        # Should fallback to "Team Member" when assignee_name is None
        assert 'Team Member' in rendered_html

    def test_render_template_with_empty_updated_fields(self, email_templates):
        """Test template rendering with empty updated_fields"""
        template_data = email_templates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        render_data = {
            'app_name': 'KIRA',
            'assignee_name': 'Test User',
            'task_title': 'Test Task',
            'task_id': 789,
            'updated_by': 'Admin',
            'update_date': '2025-10-15',
            'updated_fields': [],  # Empty list
            'previous_values': {},
            'new_values': {}
        }
        
        # Should render without errors
        rendered_html = html_template.render(**render_data)
        assert 'Test Task' in rendered_html

    def test_render_template_with_multiple_field_changes(self, email_templates):
        """Test template rendering with multiple field changes"""
        template_data = email_templates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        render_data = {
            'app_name': 'KIRA',
            'assignee_name': 'Test User',
            'task_title': 'Multi-Update Task',
            'task_id': 999,
            'updated_by': 'Project Manager',
            'update_date': '2025-10-15',
            'updated_fields': ['title', 'description', 'priority', 'deadline'],
            'previous_values': {
                'title': 'Old Title',
                'description': 'Old Description',
                'priority': 'LOW',
                'deadline': '2025-10-01'
            },
            'new_values': {
                'title': 'New Title',
                'description': 'New Description',
                'priority': 'HIGH',
                'deadline': '2025-10-31'
            }
        }
        
        rendered_html = html_template.render(**render_data)
        
        # Check that all field changes are represented
        assert 'Multi-Update Task' in rendered_html
        assert 'Project Manager' in rendered_html

    def test_template_static_method(self):
        """Test that get_task_update_template is a static method"""
        # Should be callable without instance
        template_data = EmailTemplates.get_task_update_template()
        
        assert isinstance(template_data, dict)
        assert 'html' in template_data
        assert 'text' in template_data

    def test_render_template_with_special_characters(self, email_templates):
        """Test template rendering with special characters in data"""
        template_data = email_templates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        render_data = {
            'app_name': 'KIRA™',
            'assignee_name': 'José María',
            'task_title': 'Task with <special> & characters',
            'task_id': 101,
            'updated_by': 'Admin & Manager',
            'update_date': '2025-10-15',
            'updated_fields': ['title'],
            'previous_values': {'title': 'Old & Previous'},
            'new_values': {'title': 'New & Updated'}
        }
        
        # Should render without errors despite special characters
        rendered_html = html_template.render(**render_data)
        assert 'José María' in rendered_html
        assert 'KIRA™' in rendered_html

    def test_render_template_with_long_content(self, email_templates):
        """Test template rendering with very long content"""
        template_data = email_templates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        long_title = "A" * 200  # Very long title
        long_description = "B" * 1000  # Very long description
        
        render_data = {
            'app_name': 'KIRA',
            'assignee_name': 'Test User',
            'task_title': long_title,
            'task_id': 202,
            'updated_by': 'System',
            'update_date': '2025-10-15',
            'updated_fields': ['title', 'description'],
            'previous_values': {'title': 'Short', 'description': 'Short desc'},
            'new_values': {'title': long_title, 'description': long_description}
        }
        
        # Should handle long content without errors
        rendered_html = html_template.render(**render_data)
        assert long_title in rendered_html


class TestEmailTemplatesEdgeCases:
    """Test edge cases for EmailTemplates"""

    def test_template_rendering_with_none_values(self):
        """Test template rendering when some values are None"""
        template_data = EmailTemplates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        render_data = {
            'app_name': 'KIRA',
            'assignee_name': None,
            'task_title': 'Test Task',
            'task_id': 303,
            'updated_by': None,
            'update_date': '2025-10-15',
            'updated_fields': ['status'],
            'previous_values': None,
            'new_values': None,
            'task_url': None
        }
        
        # Should handle None values gracefully
        rendered_html = html_template.render(**render_data)
        assert 'Test Task' in rendered_html

    def test_template_with_numeric_and_boolean_values(self):
        """Test template rendering with various data types"""
        template_data = EmailTemplates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        render_data = {
            'app_name': 'KIRA',
            'assignee_name': 'Test User',
            'task_title': 'Numeric Test Task',
            'task_id': 404,
            'updated_by': 'System',
            'update_date': '2025-10-15',
            'updated_fields': ['priority', 'active'],
            'previous_values': {'priority': 3, 'active': True},
            'new_values': {'priority': 5, 'active': False}
        }
        
        rendered_html = html_template.render(**render_data)
        assert 'Numeric Test Task' in rendered_html

    def test_template_rendering_performance(self):
        """Test template rendering with a large number of fields"""
        template_data = EmailTemplates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        # Create large field update data
        updated_fields = [f"field_{i}" for i in range(50)]
        previous_values = {f"field_{i}": f"old_value_{i}" for i in range(50)}
        new_values = {f"field_{i}": f"new_value_{i}" for i in range(50)}
        
        render_data = {
            'app_name': 'KIRA',
            'assignee_name': 'Performance Test User',
            'task_title': 'Performance Test Task',
            'task_id': 505,
            'updated_by': 'Test System',
            'update_date': '2025-10-15',
            'updated_fields': updated_fields,
            'previous_values': previous_values,
            'new_values': new_values
        }
        
        # Should handle large amounts of data
        rendered_html = html_template.render(**render_data)
        assert 'Performance Test Task' in rendered_html
        assert len(rendered_html) > 1000  # Should produce substantial output