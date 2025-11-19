from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional

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
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_finance_user)
):
    """
    Calculates the total income grouped by each activity for the user's club.
    Income not associated with any specific activity is grouped under 'Cuota Social'.
    Can be filtered by year and/or month.
    """
    
    # Base query for income transactions
    base_query = db.query(models.ClubTransaction).filter(
        models.ClubTransaction.club_id == current_user.club_id,
        models.ClubTransaction.type == models.CategoryType.INCOME
    )

    if year:
        base_query = base_query.filter(extract('year', models.ClubTransaction.transaction_date) == year)
    if month:
        base_query = base_query.filter(extract('month', models.ClubTransaction.transaction_date) == month)

    # Subquery for activity-related income
    activity_income_query = base_query.join(
            models.Activity, models.ClubTransaction.activity_id == models.Activity.id
        ).with_entities(
            models.Activity.name,
            func.sum(models.ClubTransaction.amount)
        ).group_by(models.Activity.name)

    income_by_activity = activity_income_query.all()

    # Query for non-activity income (base fee, others)
    base_fee_income = base_query.filter(
            models.ClubTransaction.activity_id == None
        ).with_entities(
            func.sum(models.ClubTransaction.amount)
        ).scalar()


    report = {row[0]: float(row[1]) for row in income_by_activity}
    
    if base_fee_income:
        report["Cuota Social / Otros"] = float(base_fee_income)

    return report
