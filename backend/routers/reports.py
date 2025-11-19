from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from .. import models, schemas
from ..database import get_db
from ..security import get_current_finance_user

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_current_finance_user)],
)

@router.get("/income-by-activity")
def get_income_by_activity(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_finance_user)
):
    """
    Calculates the total income grouped by each activity for the user's club.
    Income not associated with any specific activity is grouped under 'Cuota Social'.
    """
    
    income_by_activity = (
        db.query(
            models.Activity.name,
            func.sum(models.ClubTransaction.amount)
        )
        .join(models.Activity, models.ClubTransaction.activity_id == models.Activity.id)
        .filter(
            models.ClubTransaction.club_id == current_user.club_id,
            models.ClubTransaction.type == models.CategoryType.INCOME
        )
        .group_by(models.Activity.name)
        .all()
    )

    base_fee_income = (
        db.query(func.sum(models.ClubTransaction.amount))
        .filter(
            models.ClubTransaction.club_id == current_user.club_id,
            models.ClubTransaction.type == models.CategoryType.INCOME,
            models.ClubTransaction.activity_id == None
        )
        .scalar()
    )

    report = {row[0]: float(row[1]) for row in income_by_activity}
    
    if base_fee_income:
        report["Cuota Social / Otros"] = float(base_fee_income)

    return report
