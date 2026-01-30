from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.session import engine
from app.routers import auth, courses

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Course Builder API",
    description="Backend API for AI-powered course builder",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(courses.router)


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Welcome to AI Course Builder API"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
