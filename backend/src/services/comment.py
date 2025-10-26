from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.comment import Comment
from backend.src.database.models.user import User
from sqlalchemy.orm import joinedload

def add_comment(task_id: int, user_id: int, comment: str):
    with SessionLocal.begin() as db:
        new_comment = Comment(task_id=task_id, user_id=user_id, comment=comment)
        db.add(new_comment)
        db.flush()
        db.refresh(new_comment)
        
        # Load user data
        user = db.query(User).filter(User.user_id == user_id).first()
        return {
            "comment_id": new_comment.comment_id,
            "task_id": new_comment.task_id,
            "user_id": new_comment.user_id,
            "comment": new_comment.comment,
            "timestamp": new_comment.timestamp,
            "user": {
                "user_id": user.user_id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "department_id": user.department_id,
                "admin": user.admin,
            } if user else None,
        }

def get_comment(comment_id: int):
    with SessionLocal() as db:
        c = db.query(Comment).options(joinedload(Comment.user)).filter(Comment.comment_id == comment_id).first()
        if not c:
            return None
        return {
            "comment_id": c.comment_id,
            "task_id": c.task_id,
            "user_id": c.user_id,
            "comment": c.comment,
            "timestamp": c.timestamp,
            "user": {
                "user_id": c.user.user_id,
                "email": c.user.email,
                "name": c.user.name,
                "role": c.user.role,
                "department_id": c.user.department_id,
                "admin": c.user.admin,
            } if c.user else None,
        }

def list_comments(task_id: int):
    with SessionLocal() as db:
        comments = db.query(Comment).options(joinedload(Comment.user)).filter(Comment.task_id == task_id).all()
        return [
            {
                "comment_id": c.comment_id,
                "task_id": c.task_id,
                "user_id": c.user_id,
                "comment": c.comment,
                "timestamp": c.timestamp,
                "user": {
                    "user_id": c.user.user_id,
                    "email": c.user.email,
                    "name": c.user.name,
                    "role": c.user.role,
                    "department_id": c.user.department_id,
                    "admin": c.user.admin,
                } if c.user else None,
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

def list_comments_by_user(user_id: int):
    """Get all comments made by a specific user"""
    with SessionLocal() as db:
        comments = db.query(Comment).options(joinedload(Comment.user)).filter(Comment.user_id == user_id).all()
        return [
            {
                "comment_id": c.comment_id,
                "task_id": c.task_id,
                "user_id": c.user_id,
                "comment": c.comment,
                "timestamp": c.timestamp,
                "user": {
                    "user_id": c.user.user_id,
                    "email": c.user.email,
                    "name": c.user.name,
                    "role": c.user.role,
                    "department_id": c.user.department_id,
                    "admin": c.user.admin,
                } if c.user else None,
            }
            for c in comments
        ]

def get_user_comment_count(user_id: int):
    """Get the total number of comments made by a user"""
    with SessionLocal() as db:
        count = db.query(Comment).filter(Comment.user_id == user_id).count()
        return count

