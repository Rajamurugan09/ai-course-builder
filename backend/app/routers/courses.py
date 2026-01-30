from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.course import Course
from app.routers.auth import get_current_user
from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate, CourseGenerateRequest
from app.services.ollama_service import generate_course_content

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Create a new course."""
    new_course = Course(
        title=course.title,
        description=course.description,
        owner_id=current_user.id
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@router.get("/", response_model=List[CourseResponse])
def get_courses(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100
):
    """Get all courses for the current user."""
    courses = db.query(Course).filter(Course.owner_id == current_user.id).offset(skip).limit(limit).all()
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get a specific course by ID."""
    course = db.query(Course).filter(Course.id == course_id, Course.owner_id == current_user.id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Update a course."""
    course = db.query(Course).filter(Course.id == course_id, Course.owner_id == current_user.id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Update only provided fields
    if course_update.title is not None:
        course.title = course_update.title
    if course_update.description is not None:
        course.description = course_update.description
    if course_update.content is not None:
        course.content = course_update.content
    
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Delete a course."""
    course = db.query(Course).filter(Course.id == course_id, Course.owner_id == current_user.id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    db.delete(course)
    db.commit()
    return None


@router.post("/generate", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def generate_course(
    course_request: CourseGenerateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Generate course content using Ollama AI."""
    # Generate content using Ollama
    content = generate_course_content(
        title=course_request.title,
        description=course_request.description,
        prompt=course_request.prompt
    )
    
    # Create course with generated content
    new_course = Course(
        title=course_request.title,
        description=course_request.description,
        content=content,
        owner_id=current_user.id
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course
