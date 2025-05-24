from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from .. import schemas, crud

router = APIRouter(prefix="/poses", tags=["poses"])

@router.get("/", response_model=list[schemas.PoseRead])
async def read_poses(db: AsyncSession = Depends(get_db)):
    return await crud.get_poses(db)

@router.post("/", response_model=schemas.PoseRead, status_code=201)
async def add_pose(pose_in: schemas.PoseCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_pose(db, pose_in)
