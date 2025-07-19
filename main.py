import time
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from fastapi.responses import JSONResponse
from sqlmodel import Session

from db import SessionDep, create_db_and_tables
from models import BackgroundTask, TaskStatus


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown (if needed)


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/status/{task_id}")
async def get_task_status(task_id: int, session: SessionDep) -> BackgroundTask:
    bg_task = session.get(BackgroundTask, task_id)

    if not bg_task:
        raise HTTPException(status_code=404, detail="No background task found")

    return bg_task


def process_long_task(task_id: int, session: Session) -> None:
    bg_task = session.get(BackgroundTask, task_id)

    if not bg_task:
        raise HTTPException(status_code=404, detail="No background task found")

    # Do task here
    time.sleep(100)

    bg_task.status = TaskStatus.COMPLETED
    session.add(bg_task)
    session.commit()
    session.refresh(bg_task)

    print("Background task executed")


@app.post("/bg-task")
async def bg_task_demo(background_tasks: BackgroundTasks, session: SessionDep):
    bg_task = BackgroundTask()
    session.add(bg_task)
    session.commit()
    session.refresh(bg_task)

    background_tasks.add_task(process_long_task, bg_task.id, session)

    return JSONResponse(
        {"task_id": bg_task.id, "message": "Task running in background"},
        status_code=202,
    )
