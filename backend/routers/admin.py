from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import db
from auth import hash_password, require_admin, require_super_admin
from routers.images import remove_file

router = APIRouter(prefix="/api/admin", tags=["admin"])


class PasswordRequest(BaseModel):
    password: str


@router.get("/users")
def list_users(admin=Depends(require_admin)):
    with db() as conn:
        rows = conn.execute("""
            SELECT id, username, is_approved, is_admin, is_super_admin, created_at
            FROM users ORDER BY created_at DESC
        """).fetchall()
    return [dict(r) for r in rows]


@router.put("/users/{user_id}/approve")
def approve_user(user_id: int, admin=Depends(require_admin)):
    with db() as conn:
        if not conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone():
            raise HTTPException(404, "用户不存在")
        conn.execute("UPDATE users SET is_approved = 1 WHERE id = ?", (user_id,))
    return {"message": "用户已批准"}


@router.put("/users/{user_id}/reject")
def reject_user(user_id: int, admin=Depends(require_admin)):
    with db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            raise HTTPException(404, "用户不存在")
        if user["is_super_admin"]:
            raise HTTPException(400, "无法撤销超级管理员权限")
        conn.execute("UPDATE users SET is_approved = 0 WHERE id = ?", (user_id,))
    return {"message": "已撤销用户批准"}


@router.put("/users/{user_id}/toggle-admin")
def toggle_admin(user_id: int, admin=Depends(require_super_admin)):
    with db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            raise HTTPException(404, "用户不存在")
        if user["is_super_admin"]:
            raise HTTPException(400, "无法修改超级管理员的权限")
        new_val = 1 - int(user["is_admin"])
        conn.execute("UPDATE users SET is_admin = ? WHERE id = ?", (new_val, user_id))
    return {"is_admin": bool(new_val)}


@router.put("/users/{user_id}/password")
def change_password(user_id: int, req: PasswordRequest, admin=Depends(require_admin)):
    if len(req.password) < 6:
        raise HTTPException(400, "密码至少需要6个字符")
    with db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            raise HTTPException(404, "用户不存在")
        if user["is_super_admin"] and not admin["is_super_admin"]:
            raise HTTPException(403, "无权修改超级管理员密码")
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hash_password(req.password), user_id)
        )
    return {"message": "密码已修改"}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin=Depends(require_admin)):
    with db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            raise HTTPException(404, "用户不存在")
        if user["is_super_admin"]:
            raise HTTPException(400, "无法删除超级管理员")
        images = conn.execute(
            "SELECT original_path, processed_path FROM images WHERE user_id = ?", (user_id,)
        ).fetchall()
        for img in images:
            remove_file(img["original_path"])
            remove_file(img["processed_path"])
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    return {"message": "用户已删除"}


@router.get("/images")
def list_all_images(admin=Depends(require_admin)):
    with db() as conn:
        rows = conn.execute("""
            SELECT i.*, u.username
            FROM images i
            JOIN users u ON i.user_id = u.id
            ORDER BY i.created_at DESC
        """).fetchall()
    return [dict(r) for r in rows]


@router.delete("/images/{image_id}")
def admin_delete_image(image_id: int, admin=Depends(require_admin)):
    with db() as conn:
        image = conn.execute("SELECT * FROM images WHERE id = ?", (image_id,)).fetchone()
        if not image:
            raise HTTPException(404, "图片不存在")
        remove_file(image["original_path"])
        remove_file(image["processed_path"])
        conn.execute("DELETE FROM images WHERE id = ?", (image_id,))
    return {"message": "删除成功"}
