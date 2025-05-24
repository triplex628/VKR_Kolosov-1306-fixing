# server/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas, crud
from ..auth import authenticate_user, create_access_token
from ..database import get_db

router = APIRouter(tags=["auth"])


@router.post(
    "/users/",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED
)
async def register(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    exists = await crud.get_user_by_email(db, user_in.email)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован"
        )
    user = await crud.create_user(db, user_in)
    return user


@router.post(
    "/token",
    response_model=schemas.Token,
    status_code=status.HTTP_200_OK
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    # теперь ждём authenticate_user
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}
