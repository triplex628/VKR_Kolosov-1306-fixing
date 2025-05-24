from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas, crud, auth
from ..database import get_db

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post(
    "/",
    response_model=schemas.WorkoutRead,
    status_code=status.HTTP_201_CREATED
)
async def create_workout_endpoint(
    workout_in: schemas.WorkoutCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(auth.get_current_user),
):
    return await crud.create_workout(db, workout_in, current_user.id)


@router.get(
    "/",
    response_model=List[schemas.WorkoutRead]
)
async def list_workouts(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(auth.get_current_user),
):
    return await crud.get_user_workouts(db, current_user.id)


@router.get(
    "/{workout_id}",
    response_model=schemas.WorkoutRead
)
async def get_workout_endpoint(
    workout_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(auth.get_current_user),
):
    w = await crud.get_workout(db, workout_id, current_user.id)
    if not w:
        raise HTTPException(status_code=404, detail="Workout not found")
    return w


@router.delete(
    "/{workout_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_workout_endpoint(
    workout_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(auth.get_current_user),
):
    success = await crud.delete_workout(db, workout_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Workout not found")
    

@router.put(
    "/{workout_id}",
    response_model=schemas.WorkoutRead,
    status_code=status.HTTP_200_OK
)
async def update_workout_endpoint(
    workout_id: int,
    workout_in: schemas.WorkoutCreate,               # принимаем тот же schema, что и для POST
    db: AsyncSession = Depends(get_db),
    current_user = Depends(auth.get_current_user),
):
    # 1) проверяем, что план принадлежит текущему юзеру
    db_workout = await crud.get_workout(db, workout_id, current_user.id)
    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    # 2) обновляем поля
    db_workout.name = workout_in.name
    db_workout.pose_data = [item.dict() for item in workout_in.pose_data]

    # 3) сохраняем
    await db.commit()
    await db.refresh(db_workout)
    return db_workout
