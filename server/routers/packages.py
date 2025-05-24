from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, crud, models
from ..database import get_db
from ..auth import get_current_user

router = APIRouter(prefix="/packages", tags=["packages"])

@router.post("/", response_model=schemas.WorkoutPackageRead, status_code=201)
def create_package(
    pkg_in: schemas.WorkoutPackageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_workout_package(db, current_user.id, pkg_in)

@router.get("/", response_model=list[schemas.WorkoutPackageRead])
def list_packages(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.list_packages(db, current_user.id)
