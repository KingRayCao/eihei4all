import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from database import db
from auth import get_current_user
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE

router = APIRouter(prefix="/api/images", tags=["images"])


def save_upload(file: UploadFile) -> str:
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "文件大小超过限制（最大50MB）")

    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if not ext:
        # Fallback from content-type
        ct_map = {
            "image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif",
            "image/webp": ".webp", "image/bmp": ".bmp",
        }
        ext = ct_map.get(file.content_type or "", ".jpg")

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"不支持的文件格式，允许：{', '.join(ALLOWED_EXTENSIONS)}")

    filename = f"{uuid.uuid4()}{ext}"
    (UPLOAD_DIR / filename).write_bytes(content)
    return filename


def remove_file(path: Optional[str]):
    if path:
        f = UPLOAD_DIR / path
        if f.exists():
            f.unlink()


def has_file(upload: Optional[UploadFile]) -> bool:
    return bool(upload and upload.filename)


# ── Public endpoints ────────────────────────────────────────────────────────

@router.get("/gallery")
def get_gallery(hours: Optional[int] = 168):
    """Gallery / carousel: only completed images, filtered by last-modified time."""
    if hours and hours > 0:
        where = ("i.processed_path IS NOT NULL AND i.is_placeholder = 0 "
                 "AND i.updated_at >= datetime('now', 'localtime', ?)")
        params: list = [f"-{hours} hours"]
    else:
        where = "i.processed_path IS NOT NULL AND i.is_placeholder = 0"
        params = []

    with db() as conn:
        rows = conn.execute(f"""
            SELECT i.id, i.title, i.source, i.processed_path, i.updated_at,
                   u.username, u.id AS user_id
            FROM images i
            JOIN users u ON i.user_id = u.id
            WHERE {where}
            ORDER BY i.updated_at DESC
        """, params).fetchall()

    return [dict(r) for r in rows]


# ── Authenticated endpoints ──────────────────────────────────────────────────

@router.get("/all")
def get_all(user=Depends(get_current_user)):
    """Full submission table visible to all logged-in users."""
    with db() as conn:
        rows = conn.execute("""
            SELECT i.*, u.username
            FROM images i
            JOIN users u ON i.user_id = u.id
            ORDER BY i.created_at DESC
        """).fetchall()
    return [dict(r) for r in rows]


@router.get("/mine")
def get_mine(user=Depends(get_current_user)):
    with db() as conn:
        rows = conn.execute("""
            SELECT i.*, u.username
            FROM images i
            JOIN users u ON i.user_id = u.id
            WHERE i.user_id = ?
            ORDER BY i.created_at DESC
        """, (user["id"],)).fetchall()
    return [dict(r) for r in rows]


@router.post("")
async def create_image(
    title: str = Form(...),
    source: Optional[str] = Form(None),
    is_placeholder: bool = Form(False),
    original: Optional[UploadFile] = File(None),
    processed: Optional[UploadFile] = File(None),
    user=Depends(get_current_user),
):
    if not title.strip():
        raise HTTPException(400, "标题不能为空")
    if not is_placeholder and not has_file(processed):
        raise HTTPException(400, "请上传P图，或勾选「先占个坑」")

    original_path = save_upload(original) if has_file(original) else None
    processed_path = None
    if not is_placeholder and has_file(processed):
        processed_path = save_upload(processed)

    with db() as conn:
        cur = conn.execute(
            """INSERT INTO images (user_id, title, source, original_path, processed_path, is_placeholder)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user["id"], title.strip(), source or None,
             original_path, processed_path, int(is_placeholder))
        )
        image_id = cur.lastrowid
        row = conn.execute("""
            SELECT i.*, u.username FROM images i
            JOIN users u ON i.user_id = u.id WHERE i.id = ?
        """, (image_id,)).fetchone()

    return dict(row)


@router.put("/{image_id}")
async def update_image(
    image_id: int,
    title: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    clear_source: bool = Form(False),
    is_placeholder: Optional[bool] = Form(None),
    original: Optional[UploadFile] = File(None),
    processed: Optional[UploadFile] = File(None),
    user=Depends(get_current_user),
):
    with db() as conn:
        image = conn.execute("SELECT * FROM images WHERE id = ?", (image_id,)).fetchone()
        if not image:
            raise HTTPException(404, "图片不存在")
        if image["user_id"] != user["id"] and not user["is_admin"]:
            raise HTTPException(403, "无权修改此图片")

        image = dict(image)

        # Handle file replacements
        if has_file(original):
            remove_file(image["original_path"])
            image["original_path"] = save_upload(original)

        new_is_placeholder = is_placeholder if is_placeholder is not None else bool(image["is_placeholder"])

        if has_file(processed):
            remove_file(image["processed_path"])
            image["processed_path"] = save_upload(processed)
            new_is_placeholder = False  # Uploaded processed → no longer placeholder

        new_title = title.strip() if title else image["title"]
        new_source = None if clear_source else (source if source is not None else image["source"])

        conn.execute("""
            UPDATE images
            SET title=?, source=?, original_path=?, processed_path=?,
                is_placeholder=?, updated_at=datetime('now', 'localtime')
            WHERE id=?
        """, (new_title, new_source, image["original_path"], image["processed_path"],
              int(new_is_placeholder), image_id))

        row = conn.execute("""
            SELECT i.*, u.username FROM images i
            JOIN users u ON i.user_id = u.id WHERE i.id = ?
        """, (image_id,)).fetchone()

    return dict(row)


@router.delete("/{image_id}")
def delete_image(image_id: int, user=Depends(get_current_user)):
    with db() as conn:
        image = conn.execute("SELECT * FROM images WHERE id = ?", (image_id,)).fetchone()
        if not image:
            raise HTTPException(404, "图片不存在")
        if image["user_id"] != user["id"] and not user["is_admin"]:
            raise HTTPException(403, "无权删除此图片")
        remove_file(image["original_path"])
        remove_file(image["processed_path"])
        conn.execute("DELETE FROM images WHERE id = ?", (image_id,))

    return {"message": "删除成功"}
