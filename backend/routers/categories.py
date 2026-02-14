from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..security import require_roles, get_current_user

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    dependencies=[Depends(require_roles(['admin', 'tesorero']))],
)

@router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new category for the current user's club.
    """
    # Check if a category with the same name and type already exists for this club
    existing_category = db.query(models.Category).filter(
        models.Category.club_id == current_user.club_id,
        models.Category.name == category_in.name,
        models.Category.type == category_in.type
    ).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category with this name and type already exists for this club")

    db_category = models.Category(
        **category_in.model_dump(),
        club_id=current_user.club_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=List[schemas.Category])
def read_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve all categories for the current user's club.
    """
    return db.query(models.Category).filter(
        models.Category.club_id == current_user.club_id
    ).order_by(models.Category.name).all()

@router.get("/{category_id}", response_model=schemas.Category)
def read_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve a specific category by ID for the current user's club.
    """
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.club_id == current_user.club_id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.put("/{category_id}", response_model=schemas.Category)
def update_category(
    category_id: int,
    category_in: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update an existing category for the current user's club.
    """
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.club_id == current_user.club_id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a category for the current user's club.
    """
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.club_id == current_user.club_id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if there are any transactions linked to this category
    linked_transactions = db.query(models.ClubTransaction).filter(
        models.ClubTransaction.category_id == category_id
    ).first()
    if linked_transactions:
        raise HTTPException(status_code=400, detail="Cannot delete category: it is linked to existing transactions.")

    db.delete(db_category)
    db.commit()
    return
