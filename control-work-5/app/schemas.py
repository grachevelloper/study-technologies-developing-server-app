from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


TaskStatus = Literal["todo", "in_progress", "done"]
UserRole = Literal["user", "admin"]


class UserContext(BaseModel):
    id: int
    role: UserRole = "user"


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    description: Optional[str] = None
    status: TaskStatus
    priority: int = Field(ge=1, le=5)


class TaskOut(TaskCreate):
    id: int
    owner_id: int


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class HealthResponse(BaseModel):
    status: str
    env: str


class RoomUsersResponse(BaseModel):
    room_id: str
    users: list[str]


class AdminStatsResponse(BaseModel):
    total_tasks: int
    by_status: dict[TaskStatus, int]
