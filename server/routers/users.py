from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from .. import schemas, crud, auth

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.UserRead)
async def read_current_user(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):
    return current_user

@router.patch("/me", response_model=schemas.UserRead)
async def update_my_profile(
    upd: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(auth.get_current_user)
):
    user = await crud.update_user_display_name(db, current_user.id, upd.display_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
