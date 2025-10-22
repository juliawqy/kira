from enum import Enum


class NotificationType(str, Enum):
    TASK_CREATE = "task_create"
    TASK_UPDATE = "task_update"
    TASK_ASSIGN = "task_assgn"
    TASK_UNASSIGN = "task_unassgn"
    COMMENT_CREATE = "comment_create"
    COMMENT_MENTION = "comment_mention"
    COMMENT_UPDATE = "comment_update"
    DELETE_TASK = "delete_task"
    DELETE_COMMENT = "delete_comment"
