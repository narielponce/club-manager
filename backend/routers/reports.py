from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, case, extract, distinct
from typing import Optional, List

from .. import models, schemas
from ..database import get_db
from ..security import get_current_finance_user, get_current_user, require_roles

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)

@router.get("/my-students/account-status", response_model=schemas.ProfessorStudentReport, dependencies=[Depends(require_roles(['profesor']))])
def get_professor_student_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    For a professor, get a report of the account status of all their students.
    """
    # 1. Get all unique student IDs for the current professor
    student_query = db.query(models.Member.id).join(
        models.Member.activities
    ).filter(
        models.Activity.profesor_id == current_user.id
    ).distinct()
    student_ids = [s.id for s in student_query.all()]

    if not student_ids:
        return schemas.ProfessorStudentReport(students=[])

    # 2. Get all member details for these students
    students = db.query(models.Member).filter(models.Member.id.in_(student_ids)).all()
    student_map = {s.id: s for s in students}

    # 3. Get all debts for these students
    debts = db.query(
        models.Debt.member_id,
        func.sum(models.Debt.total_amount).label('total_debt')
    ).filter(
        models.Debt.member_id.in_(student_ids)
    ).group_by(models.Debt.member_id).all()
    debt_map = {d.member_id: d.total_debt for d in debts}

    # 4. Get all payments for these students
    payments = db.query(
        models.Debt.member_id,
        func.sum(models.Payment.amount).label('total_paid')
    ).join(
        models.Payment, models.Debt.id == models.Payment.debt_id
    ).filter(
        models.Debt.member_id.in_(student_ids)
    ).group_by(models.Debt.member_id).all()
    payment_map = {p.member_id: p.total_paid for p in payments}

    # 5. Build the report
    report_items = []
    for student_id in student_ids:
        total_debt = debt_map.get(student_id, 0.0)
        total_paid = payment_map.get(student_id, 0.0)
        balance = float(total_debt) - float(total_paid)
        
        student = student_map.get(student_id)
        if student:
            report_items.append(schemas.StudentAccountStatus(
                member_id=student.id,
                first_name=student.first_name,
                last_name=student.last_name,
                dni=student.dni,
                balance=balance
            ))
            
    return schemas.ProfessorStudentReport(students=report_items)


@router.get("/income-by-activity", dependencies=[Depends(get_current_finance_user)])
def get_income_by_activity(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_finance_user)
):
    """
    Calculates the total income grouped by each activity for the user's club.
    Income not associated with any specific activity is grouped under 'Cuota Social'.
    This can be filtered by year and/or month.
    """
    
    # Base filters for all income queries
    base_filters = [
        models.ClubTransaction.club_id == current_user.club_id,
        models.ClubTransaction.type == models.CategoryType.INCOME,
    ]
    if year:
        base_filters.append(extract('year', models.ClubTransaction.transaction_date) == year)
    if month:
        base_filters.append(extract('month', models.ClubTransaction.transaction_date) == month)

    # Income from specific activities
    income_by_activity = (
        db.query(
            models.Activity.name,
            func.sum(models.ClubTransaction.amount)
        )
        .join(models.Activity, models.ClubTransaction.activity_id == models.Activity.id)
        .filter(*base_filters)
        .group_by(models.Activity.name)
        .all()
    )

    # Income not tied to a specific activity (base fee, etc.)
    other_income_filters = base_filters + [models.ClubTransaction.activity_id == None]
    base_fee_income = (
        db.query(func.sum(models.ClubTransaction.amount))
        .filter(*other_income_filters)
        .scalar()
    )

    report = {row[0]: float(row[1]) for row in income_by_activity}
    
    if base_fee_income:
        report["Cuota Social / Otros"] = float(base_fee_income)

    return report

@router.get("/income-vs-expenses/{year}", response_model=schemas.IncomeVsExpensesReport, dependencies=[Depends(get_current_finance_user)])
def get_income_vs_expenses(
    year: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_finance_user)
):
    """
    Calculates the total income and expenses for each month of a given year.
    """
    # Case statements to conditionally sum income and expenses
    income_case = case((models.ClubTransaction.type == 'income', models.ClubTransaction.amount), else_=0)
    expense_case = case((models.ClubTransaction.type == 'expense', models.ClubTransaction.amount), else_=0)

    # Query to get monthly totals
    monthly_data = (
        db.query(
            extract('month', models.ClubTransaction.transaction_date).label('month_num'),
            func.sum(income_case).label('total_income'),
            func.sum(expense_case).label('total_expense')
        )
        .filter(
            models.ClubTransaction.club_id == current_user.club_id,
            extract('year', models.ClubTransaction.transaction_date) == year
        )
        .group_by('month_num')
        .order_by('month_num')
        .all()
    )

    # Create a dictionary for easy lookup
    data_map = {row.month_num: row for row in monthly_data}
    
    # Ensure all 12 months are present in the report
    report_items = []
    month_names = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    
    for i in range(1, 13):
        month_num = i
        month_name = month_names[i-1]
        
        if month_num in data_map:
            row = data_map[month_num]
            income = float(row.total_income)
            expense = float(row.total_expense)
        else:
            income = 0.0
            expense = 0.0
            
        report_items.append(schemas.MonthlyBalanceItem(
            month=month_num,
            month_name=month_name,
            income=income,
            expense=expense,
            balance=income - expense
        ))

    # Calculate annual totals
    annual_income = sum(item.income for item in report_items)
    annual_expense = sum(item.expense for item in report_items)
    annual_balance = annual_income - annual_expense

    return schemas.IncomeVsExpensesReport(
        items=report_items,
        annual_income=annual_income,
        annual_expense=annual_expense,
        annual_balance=annual_balance
    )

@router.get("/distribution-by-category", response_model=schemas.CategoryDistributionReport, dependencies=[Depends(get_current_finance_user)])
def get_distribution_by_category(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_finance_user)
):
    """
    Calculates the distribution of incomes and expenses grouped by category.
    This can be filtered by year and/or month.
    """
    # Base filters for all queries in this endpoint
    base_filters = [models.ClubTransaction.club_id == current_user.club_id]
    if year:
        base_filters.append(extract('year', models.ClubTransaction.transaction_date) == year)
    if month:
        base_filters.append(extract('month', models.ClubTransaction.transaction_date) == month)

    # Query for income distribution
    income_filters = base_filters + [models.ClubTransaction.type == models.CategoryType.INCOME]
    income_query = (
        db.query(
            models.Category.name,
            func.sum(models.ClubTransaction.amount)
        )
        .outerjoin(models.Category, models.ClubTransaction.category_id == models.Category.id)
        .filter(*income_filters)
        .group_by(models.Category.name)
        .all()
    )

    # Query for expense distribution
    expense_filters = base_filters + [models.ClubTransaction.type == models.CategoryType.EXPENSE]
    expense_query = (
        db.query(
            models.Category.name,
            func.sum(models.ClubTransaction.amount)
        )
        .outerjoin(models.Category, models.ClubTransaction.category_id == models.Category.id)
        .filter(*expense_filters)
        .group_by(models.Category.name)
        .all()
    )

    # Process results into the response model format
    income_dist = [schemas.CategoryTotalItem(category=name or "Sin Categoría", total=total) for name, total in income_query]
    expense_dist = [schemas.CategoryTotalItem(category=name or "Sin Categoría", total=total) for name, total in expense_query]

    return schemas.CategoryDistributionReport(
        income_by_category=income_dist,
        expense_by_category=expense_dist
    )
