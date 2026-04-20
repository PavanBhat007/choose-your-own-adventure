from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routers import story, job
from db.database import create_tables

create_tables()

app = FastAPI(
    title="Choose Your Own Adventure API",
    description="An API for a choose your own adventure game",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    # allowed origins that can access the API
    allow_origins=settings.ALLOWED_ORIGINS,
    # allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_methods=["*"],
    # allow all headers (Content-Type, Authorization, etc.)
    allow_headers=["*"],
    # allow anyone to send credentials (cookies, authorization headers, etc.)
    allow_credentials=True,
)

app.include_router(story.router, prefix=settings.API_PREFIX)
app.include_router(job.router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn  # allows to run the FastAPI application

    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
