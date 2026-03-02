from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import db
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(req: RegisterRequest):
    username = req.username.strip()
    if len(username) < 2 or len(username) > 20:
        raise HTTPException(400, "用户名长度需在2-20个字符之间")
    if len(req.password) < 6:
        raise HTTPException(400, "密码至少需要6个字符")

    with db() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing:
            raise HTTPException(400, "用户名已存在")
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(req.password))
        )

    return {"message": "注册成功，等待管理员审批"}


@router.post("/login")
def login(req: LoginRequest):
    with db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (req.username,)
        ).fetchone()

    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(401, "用户名或密码错误")
    if not user["is_approved"]:
        raise HTTPException(403, "账号尚未被管理员批准")

    token = create_access_token(user["id"])
    return {
        "access_token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "is_admin": bool(user["is_admin"]),
            "is_super_admin": bool(user["is_super_admin"]),
        }
    }
