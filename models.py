from sqlmodel import Field, SQLModel
from enum import Enum
from datetime import datetime, timezone


class TaskStatus(str, Enum):
    FAILED = "failed"
    PROCESSING = "processing"
    COMPLETED = "completed"


class BackgroundTask(SQLModel, table=True):
    __tablename__ = "background_tasks"

    id: int | None = Field(default=None, primary_key=True)
    status: TaskStatus = Field(default=TaskStatus.PROCESSING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
