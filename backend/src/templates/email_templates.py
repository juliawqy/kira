"""
Email templates for different notification types
"""
from jinja2 import Template
from typing import Dict, Any


class EmailTemplates:
    """Email template manager"""
    
    @staticmethod
    def get_task_update_template() -> Dict[str, str]:
        """Get task update email template"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Task Update Notification</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #007bff; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background-color: #f8f9fa; }
                .task-info { background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .changes { background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }
                .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
                .btn { display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ app_name }}</h1>
                    <h2>Task Update Notification</h2>
                </div>
                
                <div class="content">
                    <p>Hello {{ assignee_name or 'Team Member' }},</p>
                    
                    <p>The following task has been updated:</p>
                    
                    <div class="task-info">
                        <h3>{{ task_title }}</h3>
                        <p><strong>Task ID:</strong> #{{ task_id }}</p>
                        <p><strong>Updated by:</strong> {{ updated_by }}</p>
                        <p><strong>Update Date:</strong> {{ update_date }}</p>
                    </div>
                    
                    {% if updated_fields %}
                    <div class="changes">
                        <h4>Changes Made:</h4>
                        <ul>
                        {% for field in updated_fields %}
                            <li>
                                <strong>{{ field }}:</strong>
                                {% if previous_values and previous_values.get(field) %}
                                    {{ previous_values[field] }} → 
                                {% endif %}
                                {% if new_values and new_values.get(field) %}
                                    {{ new_values[field] }}
                                {% else %}
                                    Updated
                                {% endif %}
                            </li>
                        {% endfor %}
                        </ul>
                    </div>
                    {% endif %}
                    
                    {% if task_url %}
                    <p style="text-align: center; margin: 20px 0;">
                        <a href="{{ task_url }}" class="btn">View Task Details</a>
                    </p>
                    {% endif %}
                    
                    <p>This is an automated notification from {{ app_name }}.</p>
                </div>
                
                <div class="footer">
                    <p>&copy; {{ app_name }}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_template = """
        {{ app_name }} - Task Update Notification
        
        Hello {{ assignee_name or 'Team Member' }},
        
        The following task has been updated:
        
        Task: {{ task_title }}
        Task ID: #{{ task_id }}
        Updated by: {{ updated_by }}
        Update Date: {{ update_date }}
        
        {% if updated_fields %}
        Changes Made:
        {% for field in updated_fields %}
        - {{ field }}:{% if previous_values and previous_values.get(field) %} {{ previous_values[field] }} →{% endif %}{% if new_values and new_values.get(field) %} {{ new_values[field] }}{% else %} Updated{% endif %}
        {% endfor %}
        {% endif %}
        
        {% if task_url %}
        View task details: {{ task_url }}
        {% endif %}
        
        This is an automated notification from {{ app_name }}.
        """
        
        return {
            "html": html_template,
            "text": text_template
        }
    
    @staticmethod
    def render_template(template_str: str, data: Dict[str, Any]) -> str:
        """Render a template with provided data"""
        template = Template(template_str)
        return template.render(**data)
    
    @staticmethod
    def get_template_by_type(email_type: str) -> Dict[str, str]:
        """Get template by email type"""
        templates = {
            "task_updated": EmailTemplates.get_task_update_template(),
        }
        
        return templates.get(email_type, {
            "html": "<p>{{ message }}</p>",
            "text": "{{ message }}"
        })