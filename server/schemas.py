# server/schemas.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Any, Dict

from pydantic import BaseModel, EmailStr, HttpUrl, Field

from .models import RoleEnum

# ──────────────────────── Пользователь ──────────────────────────
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


# ──────────────────────── Поза / Видео ──────────────────────────
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


# ──────────────────────── Workout-package ───────────────────────
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


# ──────────────────────── Сессия и оценки ───────────────────────
class SessionPoseScoreBase(BaseModel):
    pose_id: int
    score: float


class SessionPoseScoreCreate(SessionPoseScoreBase):  # при создании
    pass


class SessionPoseScoreRead(SessionPoseScoreBase):    # при чтении
    class Config:
        orm_mode = True

class SessionPoseScoreCreate(BaseModel):
    pose_id: int
    score: float

class WorkoutSessionCreate(BaseModel):
    workout_id: Optional[int] = None
    total_time: int
    # допускаем оба варианта: pose_scores (новый) и scores (старый фронт)
    scores: List[SessionPoseScoreCreate] 

    class Config:
        allow_population_by_field_name = True


class WorkoutSessionRead(BaseModel):
    """
    Ответ при GET /sessions/
    """
    id: int
    workout_id: Optional[int] = None
    workout_name: Optional[str] = None
    started_at: datetime
    total_time: int
    avg_score: float
    scores: List[SessionPoseScoreRead]

    class Config:
        orm_mode = True


# ──────────────────────── Статистика ────────────────────────────
class StatsPoint(BaseModel):
    period_start: datetime
    avg_score: float
    total_time: int
    session_count: int


# ──────────────────────── Auth ──────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None


# ──────────────────────── Workout / Plan ────────────────────────
class PoseInPlan(BaseModel):
    pose_id: int
    duration: int
    rest: Optional[int] = None


class WorkoutCreate(BaseModel):
    name: str
    pose_data: List[PoseInPlan]


class WorkoutRead(WorkoutCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


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


# ──────────────────────── ML-эндпойнт ───────────────────────────
class PoseProcessResponse(BaseModel):
    pose_id: int
    pose_name: Optional[str] = None
    score: float
    message: Optional[str] = None

    class Config:
        orm_mode = True
