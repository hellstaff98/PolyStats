from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.authentication.fastapi_users import current_active_user
from core.config import settings
from core.models import User, db_helper, Subject, Activity
from core.schemas.activity import ActivityRead, ActivityCreate
from core.schemas.subject import SubjectRead, SubjectCreate

router = APIRouter(
    prefix=settings.api.v1.subjects,
    tags=["Subjects & progress"]
)


@router.post("/add", response_model=SubjectRead, status_code=status.HTTP_201_CREATED)
async def add_custom_subject(
    subject_data: SubjectCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter)
):
    """Добавить предмет вручную (например если не загрузился сам или нет в расписании)"""
    new_subject = Subject(
        name=subject_data.name,
        user_id=user.id
    )
    session.add(new_subject)
    await session.commit()
    await session.refresh(new_subject)

    # Формируем словарь для Pydantic
    subject_dict = {
        "id": new_subject.id,
        "name": new_subject.name,
        "user_id": new_subject.user_id,
        "activities": [],
    }
    return SubjectRead.model_validate(subject_dict)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter)
):
    """Удалить предмет целиком вместе со всеми активностями"""
    stmt = select(Subject).where(Subject.id == subject_id, Subject.user_id == user.id)
    result = await session.execute(stmt)
    subject = result.scalar_one_or_none()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Предмет не найден или доступ запрещен"
        )

    await session.delete(subject)
    await session.commit()
    return None


@router.get("/list", response_model=List[SubjectRead])
async def get_subjects_list(
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(db_helper.session_getter)
):
    """Краткий список всех предметов пользователя"""
    stmt = (
        select(Subject)
        .options(selectinload(Subject.activities))
        .where(Subject.user_id == user.id)
    )
    result = await session.execute(stmt)
    subjects = result.scalars().all()

    subjects_list = []
    for s in subjects:
        subject_dict = {
            "id": s.id,
            "name": s.name,
            "user_id": s.user_id,
            "activities": [
                ActivityRead.model_validate(a) for a in getattr(s, "activities", [])
            ]
        }
        subjects_list.append(SubjectRead.model_validate(subject_dict))

    return subjects_list


@router.get("/{subject_id}", response_model=SubjectRead)
async def get_subject_details(
        subject_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(db_helper.session_getter)
):
    """Получить подробную информацию о предмете и его активностях"""
    stmt = (
        select(Subject)
        .options(selectinload(Subject.activities))
        .where(Subject.id == subject_id, Subject.user_id == user.id)
    )
    result = await session.execute(stmt)
    subject = result.scalar_one_or_none()

    if not subject:
        raise HTTPException(status_code=404, detail="Предмет не найден")

    subject_dict = {
        "id": subject.id,
        "name": subject.name,
        "user_id": subject.user_id,
        "activities": [
            ActivityRead.model_validate(a) for a in getattr(subject, "activities", [])
        ]
    }
    return SubjectRead.model_validate(subject_dict)


@router.post("/{subject_id}/activity-add", response_model=ActivityRead)
async def add_activity_to_subject(
        subject_id: int,
        activity_data: ActivityCreate,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(db_helper.session_getter)
):
    """Добавить активность к предмету"""
    stmt = select(Subject).where(Subject.id == subject_id, Subject.user_id == user.id)
    res = await session.execute(stmt)
    if not res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Предмет не найден")

    new_act = Activity(**activity_data.model_dump(), subject_id=subject_id)
    session.add(new_act)
    await session.commit()
    await session.refresh(new_act)
    return ActivityRead.model_validate(new_act)


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
        activity_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(db_helper.session_getter)
):
    """Полностью удалить активность"""
    stmt = (
        select(Activity)
        .join(Subject)
        .where(Activity.id == activity_id, Subject.user_id == user.id)
    )
    result = await session.execute(stmt)
    activity = result.scalar_one_or_none()

    if not activity:
        raise HTTPException(status_code=404, detail="Активность не найдена или доступ запрещен")

    await session.delete(activity)
    await session.commit()
    return None


@router.patch("/activities/{activity_id}/plus", response_model=ActivityRead)
async def increment_activity_progress(
        activity_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(db_helper.session_getter)
):
    """Увеличить текущий прогресс активности на 1"""
    stmt = (
        select(Activity)
        .join(Subject)
        .where(Activity.id == activity_id, Subject.user_id == user.id)
    )
    result = await session.execute(stmt)
    activity = result.scalar_one_or_none()

    if not activity:
        raise HTTPException(status_code=404, detail="Активность не найдена")

    if activity.current_progress < activity.max_progress:
        activity.current_progress += 1
        await session.commit()
        await session.refresh(activity)

    return ActivityRead.model_validate(activity)


@router.patch("/activities/{activity_id}/minus", response_model=ActivityRead)
async def decrement_activity_progress(
        activity_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(db_helper.session_getter)
):
    """Уменьшить текущий прогресс активности на 1"""
    stmt = (
        select(Activity)
        .join(Subject)
        .where(Activity.id == activity_id, Subject.user_id == user.id)
    )
    result = await session.execute(stmt)
    activity = result.scalar_one_or_none()

    if not activity:
        raise HTTPException(status_code=404, detail="Активность не найдена")

    if activity.current_progress > 0:
        activity.current_progress -= 1
        await session.commit()
        await session.refresh(activity)

    return ActivityRead.model_validate(activity)
