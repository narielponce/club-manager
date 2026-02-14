from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles # No static files (uploads) for personal expenses
import os
from contextlib import asynccontextmanager
import locale

from . import models, database, security
from .routers import auth # Keep auth for now

# --- Lifespan Events ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("INFO:     Application startup...")
    # Set locale for Spanish month names
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        print("WARNING: Could not set locale to es_ES.UTF-8. Month names might not be in Spanish.")
    
    # The create_all call is now handled by Alembic
    # models.Base.metadata.create_all(bind=database.engine)

    # Superadmin creation logic for the SaaS platform
    db = database.SessionLocal()
    superadmin_email = os.getenv("SUPERADMIN_EMAIL")
    superadmin_password = os.getenv("SUPERADMIN_PASSWORD")

    if superadmin_email and superadmin_password:
        user = db.query(models.User).filter(models.User.email == superadmin_email).first()
        if not user:
            hashed_password = security.get_password_hash(superadmin_password)
            superadmin_user = models.User(
                email=superadmin_email,
                hashed_password=hashed_password,
                role="superadmin",
                client_id=None, # Superadmin is not tied to a client
                force_password_change=False # Explicitly set on creation
            )
            db.add(superadmin_user)
            db.commit()
            print(f"INFO:     Superadmin user '{superadmin_email}' created.")
        else:
            print(f"INFO:     Superadmin user '{superadmin_email}' already exists.")
            # Data correction for existing superadmin from older versions if needed
            if user.force_password_change is None:
                print("INFO:     Updating existing superadmin with force_password_change=False.")
                user.force_password_change = False
                db.add(user)
                db.commit()
    else:
        print("INFO:     SUPERADMIN_EMAIL or SUPERADMIN_PASSWORD not set. Skipping superadmin creation.")
    db.close()
    
    yield
    # Code to run on shutdown
    print("INFO:     Application shutdown.")

# --- App Initialization ---
app = FastAPI(lifespan=lifespan, root_path="/api")

# --- Static Files ---
# No uploads directory for this project
# os.makedirs("/code/uploads", exist_ok=True) 
# app.mount("/uploads", StaticFiles(directory="/code/uploads"), name="uploads")

# --- CORS Middleware ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
# Add frontend URL from environment variable if set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    origins.append(frontend_url)
    # Also add the URL without the port if it specifies 8080, for flexibility
    if ":8080" in frontend_url:
        origins.append(frontend_url.replace(":8080", ""))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],  # Explicitly allow Authorization
)

# --- API Routers ---
app.include_router(auth.router)
# Remove all business-specific routers from previous project
# app.include_router(members.router)
# app.include_router(users.router)
# app.include_router(activities.router)
# app.include_router(debts.router)
# app.include_router(club.router)
# app.include_router(superadmin.router)
# app.include_router(categories.router)
# app.include_router(transactions.router)
# app.include_router(reports.router)
# app.include_router(account.router)
# app.include_router(admin.router)


# --- Root Endpoint ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Personal Expense Manager API"}