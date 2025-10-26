import logging
from typing import List, Dict, Any, Optional
from backend.src.services import team as team_service
from backend.src.services import user as user_service
from backend.src.services import task as task_service
from backend.src.services import task_assignment as assignment_service
from backend.src.services.notification import get_notification_service
from backend.src.enums.notification import NotificationType
from backend.src.enums.user_role import UserRole

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# -------- Team Management Handlers -------------------------------------------------------

def create_team_with_manager(team_name: str, manager_id: int, department_id: int, team_number: str) -> Dict[str, Any]:
    """
    Create a team and assign the manager to it.
    """
    # Validate manager exists and has appropriate role
    manager = user_service.get_user(manager_id)
    if not manager:
        raise ValueError(f"Manager with id {manager_id} not found")
    
    # Check if manager has appropriate role (MANAGER or DIRECTOR)
    if manager.role not in [UserRole.MANAGER.value, UserRole.DIRECTOR.value]:
        raise ValueError(f"User {manager_id} does not have permission to create teams")
    
    # Create the team
    team = team_service.create_team(team_name, manager_id, department_id, team_number)
    
    # Automatically assign the manager to the team
    try:
        team_service.assign_to_team(team["team_id"], manager_id)
        logger.info(f"Manager {manager_id} automatically assigned to team {team['team_id']}")
    except ValueError as e:
        # Manager might already be assigned, which is fine
        logger.warning(f"Manager assignment warning: {str(e)}")
    
    return team


def get_team_with_members(team_id: int) -> Dict[str, Any]:
    """
    Get team details including all members.
    """
    team = team_service.get_team_by_id(team_id)
    if not team:
        raise ValueError(f"Team with id {team_id} not found")
    
    # Get team members
    members = team_service.get_team_members(team_id)
    team["members"] = [
        {
            "user_id": member.user_id,
            "name": member.name,
            "email": member.email,
            "role": member.role,
            "department_id": member.department_id
        }
        for member in members
    ]
    
    return team


def list_teams_with_member_counts() -> List[Dict[str, Any]]:
    """
    List all teams with member counts.
    """
    teams = team_service.list_teams()
    teams_with_counts = []
    
    for team in teams:
        member_count = len(team_service.get_team_members(team["team_id"]))
        team["member_count"] = member_count
        teams_with_counts.append(team)
    
    return teams_with_counts


def get_user_teams(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all teams that a user belongs to.
    """
    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    
    teams = team_service.get_teams_for_user(user_id)
    return [
        {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "manager_id": team.manager_id,
            "department_id": team.department_id,
            "team_number": team.team_number
        }
        for team in teams
    ]


# -------- Team Assignment Handlers -------------------------------------------------------

def assign_users_to_team_with_validation(team_id: int, user_ids: List[int], assigner_id: int) -> Dict[str, Any]:
    """
    Assign users to a team with proper validation and notifications.
    """
    # Validate team exists
    team = team_service.get_team_by_id(team_id)
    if not team:
        raise ValueError(f"Team with id {team_id} not found")
    
    # Validate assigner has permission
    assigner = user_service.get_user(assigner_id)
    if not assigner:
        raise ValueError(f"Assigner with id {assigner_id} not found")
    
    # Check if assigner is team manager or has admin privileges
    if (assigner.role not in [UserRole.MANAGER.value, UserRole.DIRECTOR.value] and 
        not assigner.admin and 
        team["manager_id"] != assigner_id):
        raise ValueError(f"User {assigner_id} does not have permission to assign users to team {team_id}")
    
    # Validate all users exist
    for user_id in user_ids:
        user = user_service.get_user(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
    
    # Perform assignment
    assigned_count = team_service.assign_users_to_team(team_id, user_ids)
    
    # Get assigned users for notification
    assigned_users = [user_service.get_user(uid) for uid in user_ids if user_service.get_user(uid)]
    
    # Send notifications to assigned users
    for user in assigned_users:
        try:
            resp = get_notification_service().notify_activity(
                user_email=assigner.email,
                task_id=None,
                task_title=f"Team Assignment: {team['team_name']}",
                type_of_alert=NotificationType.TEAM_ASSIGNMENT.value,
                updated_fields=["team_assignment"],
                old_values={},
                new_values={"team_name": team["team_name"], "team_id": team_id},
                to_recipients=[user.email] if user.email else None,
            )
            logger.info(
                f"Team assignment notification sent to user {user.user_id}",
                extra={
                    "team_id": team_id,
                    "user_id": user.user_id,
                    "assigner_id": assigner_id,
                    "success": getattr(resp, "success", None),
                }
            )
        except Exception as e:
            logger.warning(f"Failed to send team assignment notification: {str(e)}")
    
    return {
        "team_id": team_id,
        "assigned_count": assigned_count,
        "assigned_users": [
            {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email
            }
            for user in assigned_users
        ]
    }


def remove_users_from_team_with_validation(team_id: int, user_ids: List[int], remover_id: int) -> Dict[str, Any]:
    """
    Remove users from a team with proper validation and notifications.
    """
    # Validate team exists
    team = team_service.get_team_by_id(team_id)
    if not team:
        raise ValueError(f"Team with id {team_id} not found")
    
    # Validate remover has permission
    remover = user_service.get_user(remover_id)
    if not remover:
        raise ValueError(f"Remover with id {remover_id} not found")
    
    # Check if remover is team manager or has admin privileges
    if (remover.role not in [UserRole.MANAGER.value, UserRole.DIRECTOR.value] and 
        not remover.admin and 
        team["manager_id"] != remover_id):
        raise ValueError(f"User {remover_id} does not have permission to remove users from team {team_id}")
    
    # Get users before removal for notification
    removed_users = [user_service.get_user(uid) for uid in user_ids if user_service.get_user(uid)]
    
    # Perform removal
    removed_count = team_service.unassign_users_from_team(team_id, user_ids)
    
    # Send notifications to removed users
    for user in removed_users:
        try:
            resp = get_notification_service().notify_activity(
                user_email=remover.email,
                task_id=None,
                task_title=f"Team Removal: {team['team_name']}",
                type_of_alert=NotificationType.TEAM_REMOVAL.value,
                updated_fields=["team_removal"],
                old_values={"team_name": team["team_name"], "team_id": team_id},
                new_values={},
                to_recipients=[user.email] if user.email else None,
            )
            logger.info(
                f"Team removal notification sent to user {user.user_id}",
                extra={
                    "team_id": team_id,
                    "user_id": user.user_id,
                    "remover_id": remover_id,
                    "success": getattr(resp, "success", None),
                }
            )
        except Exception as e:
            logger.warning(f"Failed to send team removal notification: {str(e)}")
    
    return {
        "team_id": team_id,
        "removed_count": removed_count,
        "removed_users": [
            {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email
            }
            for user in removed_users
        ]
    }


# -------- Team-Task Integration Handlers -------------------------------------------------------

def assign_team_to_task_with_notifications(team_id: int, task_id: int, assigner_id: int) -> Dict[str, Any]:
    """
    Assign all team members to a task with notifications.
    """
    # Validate team exists
    team = team_service.get_team_by_id(team_id)
    if not team:
        raise ValueError(f"Team with id {team_id} not found")
    
    # Validate task exists
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError(f"Task with id {task_id} not found")
    
    # Validate assigner has permission
    assigner = user_service.get_user(assigner_id)
    if not assigner:
        raise ValueError(f"Assigner with id {assigner_id} not found")
    
    # Get team members before assignment
    team_members = team_service.get_team_members(team_id)
    if not team_members:
        return {"team_id": team_id, "task_id": task_id, "assigned_count": 0, "message": "No team members to assign"}
    
    # Perform assignment
    assigned_count = assignment_service.assign_team_to_task(team_id, task_id)
    
    # Send notifications to team members
    for member in team_members:
        try:
            resp = get_notification_service().notify_activity(
                user_email=assigner.email,
                task_id=task_id,
                task_title=task.title or "",
                type_of_alert=NotificationType.TASK_ASSIGNMENT.value,
                updated_fields=["task_assignment"],
                old_values={},
                new_values={"team_name": team["team_name"], "task_title": task.title or ""},
                to_recipients=[member.email] if member.email else None,
            )
            logger.info(
                f"Team task assignment notification sent to user {member.user_id}",
                extra={
                    "team_id": team_id,
                    "task_id": task_id,
                    "user_id": member.user_id,
                    "assigner_id": assigner_id,
                    "success": getattr(resp, "success", None),
                }
            )
        except Exception as e:
            logger.warning(f"Failed to send team task assignment notification: {str(e)}")
    
    return {
        "team_id": team_id,
        "task_id": task_id,
        "assigned_count": assigned_count,
        "team_name": team["team_name"],
        "task_title": task.title or ""
    }


def unassign_team_from_task_with_notifications(team_id: int, task_id: int, unassigner_id: int) -> Dict[str, Any]:
    """
    Unassign all team members from a task with notifications.
    """
    # Validate team exists
    team = team_service.get_team_by_id(team_id)
    if not team:
        raise ValueError(f"Team with id {team_id} not found")
    
    # Validate task exists
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError(f"Task with id {task_id} not found")
    
    # Validate unassigner has permission
    unassigner = user_service.get_user(unassigner_id)
    if not unassigner:
        raise ValueError(f"Unassigner with id {unassigner_id} not found")
    
    # Get team members before unassignment
    team_members = team_service.get_team_members(team_id)
    
    # Perform unassignment
    unassigned_count = assignment_service.unassign_team_from_task(team_id, task_id)
    
    # Send notifications to team members
    for member in team_members:
        try:
            resp = get_notification_service().notify_activity(
                user_email=unassigner.email,
                task_id=task_id,
                task_title=task.title or "",
                type_of_alert=NotificationType.TASK_UNASSIGNMENT.value,
                updated_fields=["task_unassignment"],
                old_values={"team_name": team["team_name"], "task_title": task.title or ""},
                new_values={},
                to_recipients=[member.email] if member.email else None,
            )
            logger.info(
                f"Team task unassignment notification sent to user {member.user_id}",
                extra={
                    "team_id": team_id,
                    "task_id": task_id,
                    "user_id": member.user_id,
                    "unassigner_id": unassigner_id,
                    "success": getattr(resp, "success", None),
                }
            )
        except Exception as e:
            logger.warning(f"Failed to send team task unassignment notification: {str(e)}")
    
    return {
        "team_id": team_id,
        "task_id": task_id,
        "unassigned_count": unassigned_count,
        "team_name": team["team_name"],
        "task_title": task.title or ""
    }


def get_task_teams_with_details(task_id: int) -> List[Dict[str, Any]]:
    """
    Get all teams assigned to a task with detailed information.
    """
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError(f"Task with id {task_id} not found")
    
    teams = assignment_service.get_teams_assigned_to_task(task_id)
    teams_with_details = []
    
    for team in teams:
        # Get team members count
        member_count = len(team_service.get_team_members(team.team_id))
        
        # Get team manager details
        manager = user_service.get_user(team.manager_id)
        
        teams_with_details.append({
            "team_id": team.team_id,
            "team_name": team.team_name,
            "manager_id": team.manager_id,
            "manager_name": manager.name if manager else "Unknown",
            "department_id": team.department_id,
            "team_number": team.team_number,
            "member_count": member_count
        })
    
    return teams_with_details


def assign_multiple_teams_to_task(team_ids: List[int], task_id: int, assigner_id: int) -> Dict[str, Any]:
    """
    Assign multiple teams to a task with notifications.
    """
    # Validate task exists
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise ValueError(f"Task with id {task_id} not found")
    
    # Validate assigner has permission
    assigner = user_service.get_user(assigner_id)
    if not assigner:
        raise ValueError(f"Assigner with id {assigner_id} not found")
    
    # Validate all teams exist
    teams_info = []
    for team_id in team_ids:
        team = team_service.get_team_by_id(team_id)
        if not team:
            raise ValueError(f"Team with id {team_id} not found")
        teams_info.append(team)
    
    # Perform assignment
    assigned_count = assignment_service.assign_users_from_teams(task_id, team_ids)
    
    # Send notifications to all team members
    total_notifications = 0
    for team in teams_info:
        team_members = team_service.get_team_members(team["team_id"])
        for member in team_members:
            try:
                resp = get_notification_service().notify_activity(
                    user_email=assigner.email,
                    task_id=task_id,
                    task_title=task.title or "",
                    type_of_alert=NotificationType.TASK_ASSIGNMENT.value,
                    updated_fields=["task_assignment"],
                    old_values={},
                    new_values={"team_name": team["team_name"], "task_title": task.title or ""},
                    to_recipients=[member.email] if member.email else None,
                )
                total_notifications += 1
                logger.info(
                    f"Multi-team task assignment notification sent to user {member.user_id}",
                    extra={
                        "team_id": team["team_id"],
                        "task_id": task_id,
                        "user_id": member.user_id,
                        "assigner_id": assigner_id,
                        "success": getattr(resp, "success", None),
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to send multi-team task assignment notification: {str(e)}")
    
    return {
        "task_id": task_id,
        "assigned_count": assigned_count,
        "teams_assigned": len(team_ids),
        "notifications_sent": total_notifications,
        "task_title": task.title or ""
    }


# -------- Team Analytics Handlers -------------------------------------------------------

def get_team_performance_summary(team_id: int) -> Dict[str, Any]:
    """
    Get a performance summary for a team including task statistics.
    """
    team = team_service.get_team_by_id(team_id)
    if not team:
        raise ValueError(f"Team with id {team_id} not found")
    
    # Get team members
    members = team_service.get_team_members(team_id)
    member_ids = [member.user_id for member in members]
    
    # Get task statistics for team members
    total_tasks = 0
    completed_tasks = 0
    active_tasks = 0
    
    for member_id in member_ids:
        member_tasks = assignment_service.list_tasks_for_user(member_id, active_only=False)
        total_tasks += len(member_tasks)
        
        for task in member_tasks:
            if task.status == "COMPLETED":
                completed_tasks += 1
            elif task.active:
                active_tasks += 1
    
    # Calculate completion rate
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return {
        "team_id": team_id,
        "team_name": team["team_name"],
        "member_count": len(members),
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "active_tasks": active_tasks,
        "completion_rate": round(completion_rate, 2)
    }


def get_user_team_workload(user_id: int) -> Dict[str, Any]:
    """
    Get workload summary for a user across all their teams.
    """
    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    
    # Get user's teams
    teams = team_service.get_teams_for_user(user_id)
    
    # Get user's tasks
    user_tasks = assignment_service.list_tasks_for_user(user_id, active_only=True)
    
    # Calculate workload by team
    team_workloads = []
    for team in teams:
        team_tasks = [task for task in user_tasks if any(
            ta.user_id == user_id for ta in task.assigned_users
        )]
        
        team_workloads.append({
            "team_id": team.team_id,
            "team_name": team.team_name,
            "task_count": len(team_tasks),
            "high_priority_tasks": len([t for t in team_tasks if t.priority >= 8]),
            "overdue_tasks": len([t for t in team_tasks if t.deadline and t.deadline < task_service.get_current_date()])
        })
    
    return {
        "user_id": user_id,
        "user_name": user.name,
        "total_teams": len(teams),
        "total_active_tasks": len(user_tasks),
        "team_workloads": team_workloads
    }
