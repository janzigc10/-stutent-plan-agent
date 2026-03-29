from typing import Optional

from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    name: str
    teacher: Optional[str] = None
    location: Optional[str] = None
    weekday: int = Field(ge=1, le=7)
    start_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    week_start: int = Field(default=1, ge=1)
    week_end: int = Field(default=16, ge=1)


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    teacher: Optional[str] = None
    location: Optional[str] = None
    weekday: Optional[int] = Field(default=None, ge=1, le=7)
    start_time: Optional[str] = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    end_time: Optional[str] = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    week_start: Optional[int] = Field(default=None, ge=1)
    week_end: Optional[int] = Field(default=None, ge=1)


class CourseOut(BaseModel):
    id: str
    user_id: str
    name: str
    teacher: Optional[str] = None
    location: Optional[str] = None
    weekday: int
    start_time: str
    end_time: str
    week_start: int
    week_end: int

    model_config = {"from_attributes": True}