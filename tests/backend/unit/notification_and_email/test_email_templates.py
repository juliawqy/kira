import pytest
from jinja2 import Template

from backend.src.templates.email_templates import EmailTemplates


class TestEmailTemplates:

    @pytest.fixture
    def email_templates(self):
        return EmailTemplates()

    # UNI-124/030
    def test_get_task_update_template_structure(self, email_templates):
        template_data = email_templates.get_task_update_template()
        
        assert isinstance(template_data, dict)
        assert 'html' in template_data
        assert 'text' in template_data
        assert isinstance(template_data['html'], str)
        assert isinstance(template_data['text'], str)

    # UNI-124/031
    def test_get_task_update_template_html_content(self, email_templates):
        template_data = email_templates.get_task_update_template()
        html_template = template_data['html']

        assert '<!DOCTYPE html>' in html_template
        assert '<html>' in html_template
        assert '<head>' in html_template
        assert '<body>' in html_template

        assert '{{ app_name }}' in html_template
        assert '{{ assignee_name' in html_template
        assert '{{ task_title }}' in html_template
        assert '{{ task_id }}' in html_template
        assert '{{ updated_by }}' in html_template
        assert '{{ update_date }}' in html_template
        assert '{% for field in updated_fields %}' in html_template

    # UNI-124/032
    def test_get_task_update_template_text_content(self, email_templates):
        template_data = email_templates.get_task_update_template()
        text_template = template_data['text']

        assert '{{ app_name }}' in text_template
        assert '{{ assignee_name' in text_template
        assert '{{ task_title }}' in text_template
        assert '{{ task_id }}' in text_template
        assert '{{ updated_by }}' in text_template
        assert '{% for field in updated_fields %}' in text_template

    # UNI-124/033
    def test_render_task_update_template_html(self, email_templates, render_data_basic):
        template_data = email_templates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        rendered_html = html_template.render(**render_data_basic)

        assert 'KIRA' in rendered_html
        assert 'John Doe' in rendered_html
        assert 'Complete Project Documentation' in rendered_html
        assert '#123' in rendered_html
        assert 'Jane Smith' in rendered_html
        assert '2025-10-15' in rendered_html

    # UNI-124/034
    def test_render_task_update_template_text(self, email_templates, render_data_basic):
        template_data = email_templates.get_task_update_template()
        text_template = Template(template_data['text'])
        
        rendered_text = text_template.render(**render_data_basic)

        assert 'KIRA' in rendered_text
        assert 'John Doe' in rendered_text
        assert 'Complete Project Documentation' in rendered_text
        assert '#123' in rendered_text
        assert 'Jane Smith' in rendered_text

    # UNI-124/035
    def test_render_template_with_missing_assignee_name(self, email_templates, render_data_missing_assignee):
        template_data = email_templates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        rendered_html = html_template.render(**render_data_missing_assignee)
        assert 'Team Member' in rendered_html

    # UNI-124/036
    def test_render_template_with_empty_updated_fields(self, email_templates, render_data_empty_fields):
        template_data = email_templates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        rendered_html = html_template.render(**render_data_empty_fields)
        assert 'Test Task' in rendered_html

    # UNI-124/037
    def test_render_template_with_multiple_field_changes(self, email_templates, render_data_multiple_changes):
        template_data = email_templates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        rendered_html = html_template.render(**render_data_multiple_changes)

        assert 'Multi-Update Task' in rendered_html
        assert 'Project Manager' in rendered_html

    # UNI-124/038
    def test_template_static_method(self):
        template_data = EmailTemplates.get_task_update_template()
        
        assert isinstance(template_data, dict)
        assert 'html' in template_data
        assert 'text' in template_data

    # UNI-124/039
    def test_render_template_with_special_characters(self, email_templates, render_data_special_chars):
        template_data = email_templates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        rendered_html = html_template.render(**render_data_special_chars)
        assert 'José María' in rendered_html
        assert 'KIRA™' in rendered_html

    # UNI-124/040
    def test_render_template_with_long_content(self, email_templates, render_data_long_content):
        template_data = email_templates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        rendered_html = html_template.render(**render_data_long_content)
        assert render_data_long_content['task_title'] in rendered_html


class TestEmailTemplatesEdgeCases:

    # UNI-124/041
    def test_template_rendering_with_none_values(self, render_data_none_values):
        template_data = EmailTemplates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        rendered_html = html_template.render(**render_data_none_values)
        assert 'Test Task' in rendered_html

    # UNI-124/042
    def test_template_with_numeric_and_boolean_values(self, render_data_numeric_boolean):
        template_data = EmailTemplates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        rendered_html = html_template.render(**render_data_numeric_boolean)
        assert 'Numeric Test Task' in rendered_html

    # UNI-124/043
    def test_template_rendering_performance(self, render_data_performance):
        template_data = EmailTemplates.get_task_update_template()
        html_template = Template(template_data['html'])
        
        rendered_html = html_template.render(**render_data_performance)
        assert 'Performance Test Task' in rendered_html
        assert len(rendered_html) > 1000