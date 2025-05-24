from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .. import schemas, crud, auth, models
from ..database import get_db

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post(
    "/",
    response_model=schemas.WorkoutSessionRead,
    status_code=status.HTTP_201_CREATED
)
async def create_session(
    sess_in: schemas.WorkoutSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return await crud.create_workout_session(db, sess_in, current_user.id)


@router.get(
    "/",
    response_model=List[schemas.WorkoutSessionRead]
)
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    sessions = await crud.get_user_sessions(db, current_user.id)
    out = []
    for s in sessions:
        out.append({
            "id":            s.id,
            "workout_id":    s.workout.id   if s.workout else None,
            "workout_name":  s.workout.name if s.workout else None,
            "started_at":    s.started_at,
            "total_time":    s.total_time,
            "avg_score":     s.avg_score,
            "scores":        s.scores,
        })
    return out
