from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from .. import schemas, crud, models
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/", response_model=list[schemas.StatsPoint])
def get_stats(
    period: str = Query("day", regex="^(day|week)$"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.stats_by_period(db, current_user.id, period)
