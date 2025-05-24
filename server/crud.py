# server/crud.py

from typing import Optional, List, Dict, Any
from sqlalchemy.future import select
from sqlalchemy import text, update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Workout
from . import models, schemas, auth
from datetime import datetime
from .schemas import WorkoutCreate

# === Пользователи ===

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(
        select(models.User).where(models.User.email == email)
    )
    return result.scalars().first()


async def create_user(
    db: AsyncSession,
    user_in: schemas.UserCreate
) -> models.User:
    hashed = auth.hash_password(user_in.password)
    user = models.User(email=user_in.email, hashed_password=hashed)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# === Workouts (ваши собственные «кастомные» тренировки) ===

async def create_workout(
    db: AsyncSession,
    workout_in: WorkoutCreate,
    user_id: int
) -> Workout:
    w = Workout(
        name=workout_in.name,
        user_id=user_id,
        pose_data=[item.dict() for item in workout_in.pose_data]
    )
    db.add(w)
    await db.commit()
    await db.refresh(w)
    return w

async def get_user_workouts(
    db: AsyncSession,
    user_id: int
) -> list[Workout]:
    res = await db.execute(
        select(Workout)
        .where(Workout.user_id == user_id)
        .order_by(Workout.created_at.desc())
    )
    return res.scalars().all()


async def get_workout(
    db: AsyncSession,
    workout_id: int,
    user_id: int
) -> Workout | None:
    res = await db.execute(
        select(Workout)
        .where(Workout.id == workout_id, Workout.user_id == user_id)
    )
    return res.scalar_one_or_none()


async def update_workout(
    db: AsyncSession,
    workout_id: int,
    user_id: int,
    name: str,
    duration: int
) -> Optional[models.Workout]:
    # Сначала находим
    workout = await get_workout(db, workout_id, user_id)
    if not workout:
        return None

    workout.name = name
    workout.duration = duration
    await db.commit()
    await db.refresh(workout)
    return workout


async def delete_workout(
    db: AsyncSession,
    workout_id: int,
    user_id: int
) -> bool:
    workout = await get_workout(db, workout_id, user_id)
    if not workout:
        return False

    await db.delete(workout)
    await db.commit()
    return True


# === Пакеты (WorkoutPackage) ===

async def create_package(
    db: AsyncSession,
    pkg_in: schemas.WorkoutPackageCreate,
    owner_id: int
) -> models.WorkoutPackage:
    pkg = models.WorkoutPackage(title=pkg_in.title, owner_id=owner_id)
    db.add(pkg)
    await db.commit()
    await db.refresh(pkg)

    # items
    for item in pkg_in.items:
        pi = models.PackageItem(
            package_id=pkg.id,
            pose_id=item.pose_id,
            repeats=item.repeats,
            duration=item.duration,
            rest=item.rest,
        )
        db.add(pi)
    await db.commit()
    return pkg


async def get_packages_for_user(
    db: AsyncSession,
    owner_id: int
) -> List[models.WorkoutPackage]:
    result = await db.execute(
        select(models.WorkoutPackage)
        .where(models.WorkoutPackage.owner_id == owner_id)
    )
    return result.scalars().all()


# === Сессии реальных тренировок ===

async def create_session(
    db: AsyncSession,
    sess_in: schemas.WorkoutSessionCreate,
    user_id: int
) -> models.WorkoutSession:
    sess = models.WorkoutSession(
        user_id=user_id,
        started_at=sess_in.started_at,
        total_time=sess_in.total_time,
    )
    db.add(sess)
    await db.commit()
    await db.refresh(sess)

    # scores
    for sc in sess_in.scores:
        sps = models.SessionPoseScore(
            session_id=sess.id,
            pose_id=sc.pose_id,
            score=sc.score,
        )
        db.add(sps)
    await db.commit()
    await db.refresh(sess)
    return sess


async def get_sessions_for_user(
    db: AsyncSession,
    user_id: int
) -> List[models.WorkoutSession]:
    result = await db.execute(
        select(models.WorkoutSession)
        .where(models.WorkoutSession.user_id == user_id)
        .options(
            # чтобы сразу подхватить scores, если нужно
        )
    )
    return result.scalars().all()


# === Статистика ===

async def stats_for_period(
    db: AsyncSession,
    user_id: int,
    period: str  # 'day' или 'week'
):
    # Пример того, как можно считать через сырые SQL:
    # 1) period_start, avg(score), sum(total_time), count(*)
    # 2) группировка по date_trunc(period, started_at)
    sql = f"""
    SELECT
      date_trunc(:period, ws.started_at) AS period_start,
      AVG(s.score) AS avg_score,
      SUM(ws.total_time) AS total_time,
      COUNT(*) AS session_count
    FROM workout_sessions ws
    JOIN session_pose_scores s ON s.session_id = ws.id
    WHERE ws.user_id = :uid
      AND ws.started_at > now() - INTERVAL '30 days'
    GROUP BY period_start
    ORDER BY period_start
    """
    result = await db.execute(
        text(sql),
        {"period": period, "uid": user_id},
    )
    return [
        {
            "period_start": row.period_start,
            "avg_score": float(row.avg_score),
            "total_time": int(row.total_time),
            "session_count": int(row.session_count),
        }
        for row in result
    ]


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Pose
from .schemas import PoseCreate

async def get_poses(db: AsyncSession):
    result = await db.execute(select(Pose))
    return result.scalars().all()

async def create_pose(db: AsyncSession, pose_in: PoseCreate):
    pose = Pose(**pose_in.dict())
    db.add(pose)
    await db.commit()
    await db.refresh(pose)
    return pose

# server/crud.py
from .models import WorkoutSession, SessionPoseScore
from .schemas import WorkoutSessionCreate
from sqlalchemy.ext.asyncio import AsyncSession

async def create_workout_session(db: AsyncSession,
                                 data: schemas.WorkoutSessionCreate,
                                 user_id: int) -> models.WorkoutSession:
    sess = models.WorkoutSession(
        user_id     = user_id,
        workout_id  = data.workout_id,
        total_time  = data.total_time
    )
    db.add(sess)
    await db.flush()                 # нужен id

    # добавляем оценки
    for item in data.scores:
        db.add(models.SessionPoseScore(
            session_id = sess.id,
            pose_id    = item.pose_id,
            score      = item.score
        ))

    # пересчитаем средний балл
    sess.avg_score = (
        sum(i.score for i in data.scores) / len(data.scores)
        if data.scores else 0
    )
    await db.commit()

    # ⬇ догружаем связь «scores» ОДНИМ запросом
    result = await db.execute(
        select(models.WorkoutSession)
        .options(selectinload(models.WorkoutSession.scores))
        .where(models.WorkoutSession.id == sess.id)
    )
    return result.scalar_one()

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from .models import WorkoutSession
from .schemas import WorkoutSessionRead

async def get_user_sessions(db: AsyncSession, user_id: int):
    q = (
        select(models.WorkoutSession)
        .where(models.WorkoutSession.user_id == user_id)
        # лениво подгружаем все оценки и сам план, чтобы не было N+1
        .options(
            selectinload(models.WorkoutSession.scores),
            selectinload(models.WorkoutSession.workout)
        )
        .order_by(models.WorkoutSession.started_at.desc())
    )
    res = await db.execute(q)
    return res.scalars().all()


async def update_user_display_name(
    db: AsyncSession,
    user_id: int,
    new_name: str
) -> models.User:
    user = await db.get(models.User, user_id)
    user.display_name = new_name
    await db.commit()
    await db.refresh(user)
    return user


