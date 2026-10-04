from fastapi import FastAPI

from database import engine, Base
from routers.location_router import router as location_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(location_router)


@app.get("/")
def home():
    return {
        "message": "Identificador de Pessoas API"
    }