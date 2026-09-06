from fastapi import FastAPI
from app.db_init import initialize_database


app = FastAPI(
    title="Barbershop API",
    version="1.0.0"
)


@app.on_event("startup")
def startup():
    initialize_database()


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }