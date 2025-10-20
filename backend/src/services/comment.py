from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.comment import Comment

def add_comment(task_id: int, user_id: int, comment: str):
    with SessionLocal.begin() as db:
        new_comment = Comment(task_id=task_id, user_id=user_id, comment=comment)
        db.add(new_comment)
        db.flush()
        db.refresh(new_comment)
        return {
            "comment_id": new_comment.comment_id,
            "task_id": new_comment.task_id,
            "user_id": new_comment.user_id,
            "comment": new_comment.comment,
            "timestamp": new_comment.timestamp,
        }

def get_comment(comment_id: int):
    with SessionLocal() as db:
        c = db.query(Comment).filter(Comment.comment_id == comment_id).first()
        if not c:
            return None
        return {
            "comment_id": c.comment_id,
            "task_id": c.task_id,
            "user_id": c.user_id,
            "comment": c.comment,
            "timestamp": c.timestamp,
        }

def list_comments(task_id: int):
    with SessionLocal() as db:
        comments = db.query(Comment).filter(Comment.task_id == task_id).all()
        return [
            {
                "comment_id": c.comment_id,
                "task_id": c.task_id,
                "user_id": c.user_id,
                "comment": c.comment,
                "timestamp": c.timestamp,
            }
            for c in comments
        ]

def update_comment(comment_id: int, updated_text: str):
    with SessionLocal.begin() as db:
        c = db.query(Comment).filter(Comment.comment_id == comment_id).first()
        if not c:
            raise ValueError("Comment not found")
        c.comment = updated_text
        db.flush()
        db.refresh(c)
        return {
            "comment_id": c.comment_id,
            "task_id": c.task_id,
            "user_id": c.user_id,
            "comment": c.comment,
            "timestamp": c.timestamp,
        }

def delete_comment(comment_id: int):
    with SessionLocal.begin() as db:
        c = db.query(Comment).filter(Comment.comment_id == comment_id).first()
        if not c:
            raise ValueError("Comment not found")
        db.delete(c)
        return True

