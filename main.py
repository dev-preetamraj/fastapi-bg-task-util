import time
from contextlib import asynccontextmanager

from celery.result import AsyncResult
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session

from celery_worker import celery_app, process_long_task_with_celery
from db import create_db_and_tables
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
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    status = task_result.status
    result = task_result.result if task_result.ready() else None

    return {"status": status, "result": result}


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
async def bg_task_demo():
    task = process_long_task_with_celery.delay()

    return JSONResponse(
        {"task_id": task.id, "message": "Task running in background"},
        status_code=202,
    )
