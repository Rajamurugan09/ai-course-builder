from typing import Optional
from pydantic import BaseModel


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None


class CourseResponse(CourseBase):
    id: int
    content: Optional[str] = None
    owner_id: int
    
    class Config:
        from_attributes = True


class CourseGenerateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    prompt: Optional[str] = None
