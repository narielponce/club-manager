from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import csv
import zipfile
import tempfile
from datetime import datetime

from ..security import require_roles, get_current_user
from .. import models, database

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_roles(['admin']))],
)

# List of models to be exported for a club
# This defines which data is considered part of a club's backup
MODELS_TO_EXPORT = [
    models.User,
    models.Activity,
    models.Member,
    models.Category,
    models.ClubTransaction,
    models.Debt,
    models.DebtItem,
    models.Payment
]

@router.get("/db-backup-csv")
async def get_db_backup_csv(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Generates a backup of all club-specific data into multiple CSV files,
    zips them, and returns the zip archive for download. Admin only.
    """
    club_id = current_user.club_id
    timestamp = datetime.now().strftime("%Y-%m-%d")

    # Use a temporary directory that cleans itself up
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # --- 1. Generate a CSV file for each model ---
        for model in MODELS_TO_EXPORT:
            table_name = model.__tablename__
            file_path = os.path.join(temp_dir, f"{table_name}.csv")
            
            # Query data for the current club
            query = db.query(model)
            # All our exportable models have a 'club_id' or a relationship to it
            if hasattr(model, 'club_id'):
                query = query.filter(model.club_id == club_id)
            elif hasattr(model, 'member'): # For Debt, DebtItem, Payment
                query = query.join(models.Member).filter(models.Member.club_id == club_id)
            
            records = query.all()
            
            if not records:
                continue # Skip creating empty files

            # Get headers from the model's table columns
            headers = [c.name for c in model.__table__.columns]
            
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    # Write header
                    writer.writerow(headers)
                    # Write data rows
                    for record in records:
                        writer.writerow([getattr(record, h, '') for h in headers])
            except IOError as e:
                raise HTTPException(status_code=500, detail=f"Failed to write CSV file for {table_name}: {e}")

        # --- 2. Create a Zip archive of the CSV files ---
        zip_filename = f"backup_club_{club_id}_{timestamp}.zip"
        zip_path = os.path.join(tempfile.gettempdir(), zip_filename)

        try:
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), arcname=file)
        except (IOError, zipfile.BadZipFile) as e:
            raise HTTPException(status_code=500, detail=f"Failed to create zip archive: {e}")

        if not os.path.exists(zip_path) or os.path.getsize(zip_path) == 0:
            raise HTTPException(status_code=404, detail="No data to backup.")
            
        # --- 3. Return the Zip file for download ---
        return FileResponse(
            path=zip_path,
            filename=zip_filename,
            media_type="application/zip",
            background=lambda: os.remove(zip_path) # Clean up the zip file
        )
