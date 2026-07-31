from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional

from .. import models, schemas
from ..database import get_db
from ..security import get_current_user, require_roles

router = APIRouter(
    tags=["schedules"],
)

# --- Physical Spaces Endpoints ---

@router.get("/physical-spaces/", response_model=List[schemas.PhysicalSpace])
def get_physical_spaces(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all physical spaces for the user's club."""
    return db.query(models.PhysicalSpace).filter(
        models.PhysicalSpace.club_id == current_user.club_id
    ).all()

@router.post("/physical-spaces/", response_model=schemas.PhysicalSpace)
def create_physical_space(
    space: schemas.PhysicalSpaceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin", "tesorero"]))
):
    """Create a new physical space."""
    db_space = models.PhysicalSpace(
        name=space.name,
        description=space.description,
        capacity=space.capacity,
        club_id=current_user.club_id
    )
    db.add(db_space)
    db.commit()
    db.refresh(db_space)
    return db_space

@router.delete("/physical-spaces/{space_id}", status_code=204)
def delete_physical_space(
    space_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin", "tesorero"]))
):
    """Delete a physical space."""
    db_space = db.query(models.PhysicalSpace).filter(
        models.PhysicalSpace.id == space_id,
        models.PhysicalSpace.club_id == current_user.club_id
    ).first()
    if not db_space:
        raise HTTPException(status_code=404, detail="Physical space not found")
    
    db.delete(db_space)
    db.commit()
    return None

# --- Schedules Endpoints ---

@router.get("/schedules/", response_model=List[schemas.ClassSchedule])
def get_schedules(
    space_id: Optional[int] = None,
    activity_id: Optional[int] = None,
    profesor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get schedules, optionally filtered by space, activity, or professor."""
    query = db.query(models.ClassSchedule).options(
        selectinload(models.ClassSchedule.activity).selectinload(models.Activity.profesor),
        selectinload(models.ClassSchedule.activity).selectinload(models.Activity.members),
        selectinload(models.ClassSchedule.space)
    ).filter(
        models.ClassSchedule.club_id == current_user.club_id
    )

    if space_id is not None:
        query = query.filter(models.ClassSchedule.space_id == space_id)
    if activity_id is not None:
        query = query.filter(models.ClassSchedule.activity_id == activity_id)
    if profesor_id is not None:
        query = query.join(models.Activity).filter(models.Activity.profesor_id == profesor_id)

    return query.all()

@router.post("/schedules/", response_model=schemas.ClassSchedule)
def create_schedule(
    schedule: schemas.ClassScheduleCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new class schedule with collision detection."""
    # 1. Verify space exists and belongs to the club
    db_space = db.query(models.PhysicalSpace).filter(
        models.PhysicalSpace.id == schedule.space_id,
        models.PhysicalSpace.club_id == current_user.club_id
    ).first()
    if not db_space:
        raise HTTPException(status_code=404, detail="Physical space not found")

    # 2. Verify activity exists and belongs to the club
    db_activity = db.query(models.Activity).options(selectinload(models.Activity.profesor)).filter(
        models.Activity.id == schedule.activity_id,
        models.Activity.club_id == current_user.club_id
    ).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # If user is a professor, verify they are assigned to this activity
    if current_user.role == "profesor" and db_activity.profesor_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para agendar horarios en una actividad que no dictas.")

    if schedule.start_time >= schedule.end_time:
        raise HTTPException(status_code=400, detail="La hora de inicio debe ser anterior a la hora de fin.")

    # 3. Collision Check: Physical Space overlap
    overlapping_space = db.query(models.ClassSchedule).filter(
        models.ClassSchedule.space_id == schedule.space_id,
        models.ClassSchedule.day_of_week == schedule.day_of_week,
        models.ClassSchedule.club_id == current_user.club_id,
        models.ClassSchedule.start_time < schedule.end_time,
        models.ClassSchedule.end_time > schedule.start_time
    ).first()
    if overlapping_space:
        raise HTTPException(
            status_code=400,
            detail=f"Superposición de espacio: El espacio '{db_space.name}' ya está reservado de {overlapping_space.start_time.strftime('%H:%M')} a {overlapping_space.end_time.strftime('%H:%M')}."
        )

    # 4. Collision Check: Professor schedule overlap
    if db_activity.profesor_id is not None:
        overlapping_prof = db.query(models.ClassSchedule).join(models.Activity).filter(
            models.Activity.profesor_id == db_activity.profesor_id,
            models.ClassSchedule.day_of_week == schedule.day_of_week,
            models.ClassSchedule.club_id == current_user.club_id,
            models.ClassSchedule.start_time < schedule.end_time,
            models.ClassSchedule.end_time > schedule.start_time
        ).first()
        if overlapping_prof:
            raise HTTPException(
                status_code=400,
                detail=f"Superposición de docente: El profesor ya tiene otra clase asignada de {overlapping_prof.start_time.strftime('%H:%M')} a {overlapping_prof.end_time.strftime('%H:%M')}."
            )

    # 5. Create Schedule
    db_schedule = models.ClassSchedule(
        activity_id=schedule.activity_id,
        space_id=schedule.space_id,
        day_of_week=schedule.day_of_week,
        start_time=schedule.start_time,
        end_time=schedule.end_time,
        club_id=current_user.club_id
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)

    # Reload with eager loaded items
    db_schedule = db.query(models.ClassSchedule).options(
        selectinload(models.ClassSchedule.activity).selectinload(models.Activity.profesor),
        selectinload(models.ClassSchedule.activity).selectinload(models.Activity.members),
        selectinload(models.ClassSchedule.space)
    ).filter(models.ClassSchedule.id == db_schedule.id).first()

    return db_schedule

@router.delete("/schedules/{schedule_id}", status_code=204)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a scheduled slot."""
    db_schedule = db.query(models.ClassSchedule).options(selectinload(models.ClassSchedule.activity)).filter(
        models.ClassSchedule.id == schedule_id,
        models.ClassSchedule.club_id == current_user.club_id
    ).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule slot not found")

    # If user is professor, verify they teach the activity
    if current_user.role == "profesor" and db_schedule.activity.profesor_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes autorización para eliminar horarios de esta actividad.")

    db.delete(db_schedule)
    db.commit()
    return None
