# server/schemas.py

from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, HttpUrl
from .models import RoleEnum

class UserBase(BaseModel):
    email: str
    display_name: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: RoleEnum
    display_name: str
    class Config:
        orm_mode = True


class UserUpdate(BaseModel):

    display_name: str

# -- поза --
class PoseBase(BaseModel):
    name: str
    description: Optional[str] = None

class PoseRead(PoseBase):
    id: int
    video_url: HttpUrl
    class Config:
        orm_mode = True

class PoseCreate(PoseBase):
    video_url: HttpUrl
# -- пакет --
class PackageItemBase(BaseModel):
    pose_id: int
    repeats: int
    duration: int
    rest: int

class WorkoutPackageCreate(BaseModel):
    title: str
    items: List[PackageItemBase]

class PackageItemRead(PackageItemBase):
    pose: PoseRead
    class Config:
        orm_mode = True

class WorkoutPackageRead(BaseModel):
    id: int
    title: str
    items: List[PackageItemRead]
    class Config:
        orm_mode = True

# -- сессия и оценки --
class SessionPoseScoreBase(BaseModel):
    pose_id: int
    score: float



class SessionPoseScoreRead(BaseModel):
    pose_id: int
    score: float
    class Config:
        orm_mode = True



# -- статистика --
class StatsPoint(BaseModel):
    period_start: datetime   # начало дня/недели
    avg_score: float
    total_time: int
    session_count: int


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None

class PoseInPlan(BaseModel):
    pose_id: int
    duration: int
    rest: Optional[int] = None   # <- теперь его можно не указывать в JSON



class WorkoutCreate(BaseModel):
    name: str
    pose_data: List[PoseInPlan]

class WorkoutRead(WorkoutCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
# Ответная схема — та, что используется в response_model
class WorkoutResponse(BaseModel):
    id: int
    name: str
    duration: int
    user_id: int
    pose_data: Optional[Dict[str, Any]] = None
    score: Optional[float] = None
    created_at: datetime

    class Config:
        orm_mode = True

class PoseProcessResponse(BaseModel):
    """
    Ответ от ML-эндпойнта по обработке позы:
    - pose_id: идентификатор распознанной позы
    - pose_name: название распознанной позы (если есть)
    - score: confidence / точность в [0.0–1.0]
    - message: опциональное текстовое пояснение
    """
    pose_id: int
    pose_name: Optional[str] = None
    score: float
    message: Optional[str] = None

    class Config:
        orm_mode = True


# server/schemas.py
from pydantic import BaseModel
from typing import List

class SessionPoseScore(BaseModel):
    pose_id: int
    score: float

    class Config:
        orm_mode = True

class SessionPoseScoreCreate(BaseModel):
    pose_id: int
    score: float

class WorkoutSessionCreate(BaseModel):
    workout_id: Optional[int] = None
    total_time: int
    pose_scores: List[SessionPoseScoreCreate]

class WorkoutSessionRead(BaseModel):
    id: int
    workout_id: int              # <— добавили
    workout_name: str
    started_at: datetime
    total_time: float
    avg_score: float
    scores: list[SessionPoseScoreCreate]

    class Config:
        orm_mode = True

