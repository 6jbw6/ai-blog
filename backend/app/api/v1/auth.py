from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token
from app.core.response import Result, BusinessException
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister, UserOut, TokenOut

router = APIRouter(prefix="/auth", tags=["认证鉴权 (Auth)"])


@router.post("/login", response_model=Result[TokenOut], summary="用户与管理员登录")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    if login_data.username.lower() == "admin":
        user = db.query(User).filter((User.username == "admin") | (User.role == "admin")).first()
    else:
        user = db.query(User).filter(
            (User.username == login_data.username) | (User.email == login_data.username)
        ).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise BusinessException("用户名或密码错误", code=400)

    if not user.is_active:
        raise BusinessException("该账号已被禁用", code=403)

    token = create_access_token(data={"sub": user.username, "role": user.role, "id": user.id})
    return Result.success(data=TokenOut(access_token=token, user=UserOut.model_validate(user)))


@router.post("/register", response_model=Result[UserOut], summary="读者注册")
def register(reg_data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == reg_data.username) | (User.email == reg_data.email)
    ).first()
    if existing:
        raise BusinessException("用户名或电子邮箱已存在", code=400)

    new_user = User(
        username=reg_data.username,
        email=reg_data.email,
        password_hash=hash_password(reg_data.password),
        nickname=reg_data.nickname or reg_data.username,
        role="reader"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return Result.success(data=UserOut.model_validate(new_user), message="注册成功")


@router.get("/me", response_model=Result[UserOut], summary="获取当前登录用户信息")
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return Result.success(data=UserOut.model_validate(current_user))
