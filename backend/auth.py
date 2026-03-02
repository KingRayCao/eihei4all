from datetime import datetime, timedelta
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_DAYS

bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="无效的令牌")

    from database import db
    with db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    if not user["is_approved"]:
        raise HTTPException(status_code=403, detail="账号尚未被批准")

    return dict(user)


def require_admin(user=Depends(get_current_user)):
    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


def require_super_admin(user=Depends(get_current_user)):
    if not user["is_super_admin"]:
        raise HTTPException(status_code=403, detail="需要超级管理员权限")
    return user
