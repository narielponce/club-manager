from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models, database
from .routers import members, auth, users, activities, debts, club


models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

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


@app.get("/")
def read_root():
    return {"message": "Welcome to the Club Manager API"}



