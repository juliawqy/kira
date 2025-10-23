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

    def verb(self) -> str:
        mapping = {
            NotificationType.TASK_CREATE: "created",
            NotificationType.TASK_UPDATE: "updated",
            NotificationType.TASK_ASSIGN: "assigned",
            NotificationType.TASK_UNASSIGN: "unassigned",
            NotificationType.COMMENT_CREATE: "commented",
            NotificationType.COMMENT_MENTION: "mentioned",
            NotificationType.COMMENT_UPDATE: "updated comment",
            NotificationType.DELETE_TASK: "deleted task",
            NotificationType.DELETE_COMMENT: "deleted comment",
        }
        return mapping.get(self, self.value)
