# server/models.py

from datetime import datetime
import enum

from sqlalchemy import (
    Column, Integer, String, ForeignKey,
    JSON, Float, DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SqlEnum

from .database import Base


class RoleEnum(str, enum.Enum):
    admin   = "admin"
    trainer = "trainer"
    doctor  = "doctor"
    user    = "user"


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role            = Column(
        SqlEnum(RoleEnum, name="role_enum", native_enum=False),
        default=RoleEnum.user,
        nullable=False
    )
    display_name    = Column(String, nullable=False)

    # связи
    workouts = relationship(
        "Workout",
        back_populates="user",
        cascade="all, delete",
    )
    sessions = relationship(
        "WorkoutSession",
        back_populates="user",
        cascade="all, delete",
    )


class Workout(Base):
    __tablename__ = "workouts"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    pose_data  = Column(JSON, nullable=True)  # [{pose_id, duration, rest}, …]
    created_at = Column(DateTime, default=datetime.utcnow)

    # связи
    user     = relationship("User", back_populates="workouts")
    sessions = relationship(
        "WorkoutSession",
        back_populates="workout",
        cascade="all, delete",
    )


class Pose(Base):
    __tablename__ = "poses"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    video_url   = Column(String, nullable=False)

    pose_scores = relationship(
        "SessionPoseScore",
        back_populates="pose",
        cascade="all, delete",
    )


class WorkoutPackage(Base):
    __tablename__ = "workout_packages"

    id       = Column(Integer, primary_key=True, index=True)
    title    = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User")
    items = relationship(
        "PackageItem",
        back_populates="package",
        cascade="all, delete",
    )


class PackageItem(Base):
    __tablename__ = "package_items"

    package_id = Column(Integer, ForeignKey("workout_packages.id"), primary_key=True)
    pose_id    = Column(Integer, ForeignKey("poses.id"), primary_key=True)
    repeats    = Column(Integer, default=1)
    duration   = Column(Integer, default=0)
    rest       = Column(Integer, default=0)

    package = relationship("WorkoutPackage", back_populates="items")
    pose    = relationship("Pose")


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_id  = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    started_at  = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_time  = Column(Integer, nullable=False)  # секунды
    avg_score   = Column(Float, nullable=True)

    # связи
    user    = relationship("User", back_populates="sessions")
    workout = relationship("Workout", back_populates="sessions")
    scores  = relationship(
        "SessionPoseScore",
        back_populates="session",
        cascade="all, delete",
    )


class SessionPoseScore(Base):
    __tablename__ = "session_pose_scores"

    session_id = Column(Integer, ForeignKey("workout_sessions.id"), primary_key=True)
    pose_id    = Column(Integer, ForeignKey("poses.id"), primary_key=True)
    score      = Column(Float, nullable=False)

    session = relationship("WorkoutSession", back_populates="scores")
    pose    = relationship("Pose", back_populates="pose_scores")
