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
    def get_upcoming_deadline_template() -> Dict[str, str]:
        """Get upcoming deadline email template"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Upcoming Deadline</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #ffc107; color: #212529; padding: 20px; text-align: center; }
                .content { padding: 20px; background-color: #f8f9fa; }
                .task-info { background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #ffc107; }
                .warning { background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; border: 1px solid #ffeaa7; }
                .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
                .btn { display: inline-block; padding: 10px 20px; background-color: #ffc107; color: #212529; text-decoration: none; border-radius: 5px; font-weight: bold; }
                .deadline-text { font-size: 18px; font-weight: bold; color: #856404; }
                .time-remaining { font-size: 16px; color: #6c757d; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ app_name }}</h1>
                    <h2>⏰ Upcoming Deadline</h2>
                </div>
                
                <div class="content">
                    <p>Hello {{ assignee_name or 'Team Member' }},</p>
                    
                    <div class="warning">
                        <p class="deadline-text">⚠️ Task deadline approaching!</p>
                        <p class="time-remaining">Due in {{ time_until_deadline }}</p>
                    </div>
                    
                    <div class="task-info">
                        <h3>{{ task_title }}</h3>
                        <p><strong>Task ID:</strong> #{{ task_id }}</p>
                        <p><strong>Deadline:</strong> {{ deadline_date }}</p>
                        <p><strong>Priority:</strong> {{ priority }}</p>
                        {% if description %}
                        <p><strong>Description:</strong> {{ description }}</p>
                        {% endif %}
                        {% if project_name %}
                        <p><strong>Project:</strong> {{ project_name }}</p>
                        {% endif %}
                        {% if custom_message %}
                        <p><strong>Note:</strong> {{ custom_message }}</p>
                        {% endif %}
                    </div>
                    
                    {% if task_url %}
                    <p style="text-align: center; margin: 20px 0;">
                        <a href="{{ task_url }}" class="btn">View Task Details</a>
                    </p>
                    {% endif %}
                    
                    <p>Please ensure this task is completed by the deadline to stay on track with your project goals.</p>
                    
                    <p>This is an automated reminder from {{ app_name }}.</p>
                </div>
                
                <div class="footer">
                    <p>&copy; {{ app_name }}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_template = """
        {{ app_name }} - Upcoming Deadline
        
        Hello {{ assignee_name or 'Team Member' }},
        
        ⚠️ TASK DEADLINE APPROACHING!
        Due in {{ time_until_deadline }}
        
        Task: {{ task_title }}
        Task ID: #{{ task_id }}
        Deadline: {{ deadline_date }}
        Priority: {{ priority }}
        {% if description %}
        Description: {{ description }}
        {% endif %}
        {% if project_name %}
        Project: {{ project_name }}
        {% endif %}
        {% if custom_message %}
        Note: {{ custom_message }}
        {% endif %}
        
        {% if task_url %}
        View task details: {{ task_url }}
        {% endif %}
        
        Please ensure this task is completed by the deadline to stay on track with your project goals.
        
        This is an automated reminder from {{ app_name }}.
        """
        
        return {
            "html": html_template,
            "text": text_template
        }
    
    @staticmethod
    def get_overdue_deadline_template() -> Dict[str, str]:
        """Get overdue deadline email template"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Overdue Task</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #dc3545; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background-color: #f8f9fa; }
                .task-info { background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #dc3545; }
                .urgent { background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 15px 0; border: 1px solid #f5c6cb; }
                .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
                .btn { display: inline-block; padding: 10px 20px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; }
                .overdue-text { font-size: 18px; font-weight: bold; color: #721c24; }
                .days-overdue { font-size: 16px; color: #6c757d; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ app_name }}</h1>
                    <h2>🚨 Overdue Task</h2>
                </div>
                
                <div class="content">
                    <p>Hello {{ assignee_name or 'Team Member' }},</p>
                    
                    <div class="urgent">
                        <p class="overdue-text">🚨 TASK IS OVERDUE!</p>
                        <p class="days-overdue">Overdue by {{ days_overdue }}</p>
                    </div>
                    
                    <div class="task-info">
                        <h3>{{ task_title }}</h3>
                        <p><strong>Task ID:</strong> #{{ task_id }}</p>
                        <p><strong>Original Deadline:</strong> {{ deadline_date }}</p>
                        <p><strong>Priority:</strong> {{ priority }}</p>
                        {% if description %}
                        <p><strong>Description:</strong> {{ description }}</p>
                        {% endif %}
                        {% if project_name %}
                        <p><strong>Project:</strong> {{ project_name }}</p>
                        {% endif %}
                        {% if custom_message %}
                        <p><strong>Note:</strong> {{ custom_message }}</p>
                        {% endif %}
                    </div>
                    
                    {% if task_url %}
                    <p style="text-align: center; margin: 20px 0;">
                        <a href="{{ task_url }}" class="btn">View Task Details</a>
                    </p>
                    {% endif %}
                    
                    <p><strong>Action Required:</strong> Please complete this task as soon as possible and update its status.</p>
                    
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
        {{ app_name }} - Overdue Task
        
        Hello {{ assignee_name or 'Team Member' }},
        
        🚨 TASK IS OVERDUE!
        Overdue by {{ days_overdue }}
        
        Task: {{ task_title }}
        Task ID: #{{ task_id }}
        Original Deadline: {{ deadline_date }}
        Priority: {{ priority }}
        {% if description %}
        Description: {{ description }}
        {% endif %}
        {% if project_name %}
        Project: {{ project_name }}
        {% endif %}
        {% if custom_message %}
        Note: {{ custom_message }}
        {% endif %}
        
        {% if task_url %}
        View task details: {{ task_url }}
        {% endif %}
        
        ACTION REQUIRED: Please complete this task as soon as possible and update its status.
        
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
            "upcoming_deadline": EmailTemplates.get_upcoming_deadline_template(),
            "overdue_deadline": EmailTemplates.get_overdue_deadline_template(),
        }
        
        return templates.get(email_type, {
            "html": "<p>{{ message }}</p>",
            "text": "{{ message }}"
        })