from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager
import locale # Added this import

from . import models, database, security
from .routers import members, auth, users, activities, debts, club, superadmin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("INFO:     Application startup...")
    # Set locale for Spanish month names
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        print("WARNING: Could not set locale to es_ES.UTF-8. Month names might not be in Spanish.")
    db = database.SessionLocal()
    try:
        # Create all tables
        models.Base.metadata.create_all(bind=database.engine)

        # Create superadmin on first startup
        superadmin_email = os.getenv("SUPERADMIN_EMAIL")
        superadmin_password = os.getenv("SUPERADMIN_PASSWORD")

        if superadmin_email and superadmin_password:
            user = db.query(models.User).filter(models.User.email == superadmin_email).first()
            if not user:
                hashed_password = security.get_password_hash(superadmin_password)
                # Superadmin does not belong to a club, so club_id is None
                superadmin_user = models.User(
                    email=superadmin_email,
                    hashed_password=hashed_password,
                    role="superadmin",
                    club_id=None  # Superadmin is not tied to any specific club
                )
                db.add(superadmin_user)
                db.commit()
                print(f"INFO:     Superadmin user '{superadmin_email}' created.")
            else:
                print(f"INFO:     Superadmin user '{superadmin_email}' already exists.")
        else:
            print("INFO:     SUPERADMIN_EMAIL or SUPERADMIN_PASSWORD not set. Skipping superadmin creation.")

    finally:
        db.close()
    
    yield
    # Code to run on shutdown
    print("INFO:     Application shutdown.")


app = FastAPI(lifespan=lifespan)

# --- CORS Middleware ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],  # Explicitly allow Authorization
)





app.include_router(members.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(activities.router)
app.include_router(debts.router)
app.include_router(club.router)
app.include_router(superadmin.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Club Manager API"}



