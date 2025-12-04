# main.py

from fastapi import FastAPI
from apps.routers import router
from database.models import Base
from database.connection import engine
from fastapi.middleware.cors import CORSMiddleware
from loggers.logger import setup_logger


app = FastAPI(title=" MarkTine API", 
              version="1.0.0", 
              description="API for managing users and marktine system.",
              contact={
                  "name": "Support Team",})

setup_logger("api")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables once on startup
Base.metadata.create_all(bind=engine)
app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Marktine API!"}