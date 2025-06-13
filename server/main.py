import asyncio
import io
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Dict
from functools import wraps
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException, Header, Query
from fastapi.responses import FileResponse

from application.model import Model, FileReader, ExcelExporter


async def clear_inactive_sessions():
    while True:
        now = datetime.now()
        to_delete = []
        for session_id, info in session_data.items():
            if now - info["last_activity"] > timedelta(minutes=5):
                to_delete.append(session_id)
        for sid in to_delete:
            del session_data[sid]
            print(f"Session {sid} has been removed due to inactivity.")
        await asyncio.sleep(60)  # каждые 60 секунд проверка

@asynccontextmanager
async def lifespan(application: FastAPI):
    task = asyncio.create_task(clear_inactive_sessions())

    yield

    task.cancel()

app = FastAPI(lifespan=lifespan)
session_data: Dict[str, Dict[str, Model | datetime]] = dict()
root_key = 1221

def admin_required(expected_key: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, master_key: int = Query(...), **kwargs):
            if master_key != expected_key:
                raise HTTPException(status_code=403, detail="Forbidden: Invalid master key")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_new_model() -> Model:
    return Model(FileReader(), ExcelExporter())

def generate_unique_session():
    while True:
        session_id = uuid.uuid4().hex
        if session_id not in session_data:
            return session_id

def update_session_activity(session_id: str):
    if session_id in session_data:
        session_data[session_id]["last_activity"] = datetime.now()

@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}

# ----------- root endpoints DELETE IN FUTURE

@app.get("/root/session")
@admin_required(root_key)
def get_all_sessions(master_key: int = Query(...)):
    return session_data

@app.get("/root/time")
@admin_required(root_key)
def get_time_all_sessions(master_key: int = Query(...)):
    return [f"До конца сессии {session[0]} осталось {timedelta(minutes=5) - (datetime.now() - session[-1]["last_activity"])}" for session in session_data.items()]

@app.delete("/root/close")
@admin_required(root_key)
def close_session_root(master_key: int = Query(...), session_id: str = Query(...)):
    session_data.pop(session_id, None)
    return {"message": f"Session: {session_id} has been deleted"}

# ------------ Normal endpoints ------------

@app.post("/session/create")
def create_session():
    session_id = generate_unique_session()
    session_data[session_id] = {
        "model": get_new_model(),
        "last_activity": datetime.now()
    }
    return {"session_id": session_id}

@app.delete("/session/close")
def close_session(authorization: str = Header(...)):
    if authorization not in session_data:
        raise HTTPException(status_code=401, detail="Invalid session")

    session_data.pop(authorization, None)
    return {"message": f"Session: {authorization} close successfully"}

@app.delete("/data")
def clear_data(authorization: str = Header(...)):
    if authorization not in session_data:
        raise HTTPException(status_code=401, detail="Invalid session")

    session_data[authorization]["model"].clear_data()

    update_session_activity(authorization)
    return {"message": "Data has been deleted successfully"}

@app.delete("/data/{item_id}")
def delete_elem_from_data(item_id: int, authorization: str = Header(...)):
    if authorization not in session_data:
        raise HTTPException(status_code=401, detail="Invalid session")

    update_session_activity(authorization)
    return f"Delete field: {item_id} Data: {session_data[authorization]["model"].data.pop(item_id)}"

@app.get("/data")
def get_data(authorization: str = Header(...)):
    if authorization not in session_data:
        raise HTTPException(status_code=401, detail="Invalid session")

    update_session_activity(authorization)
    return session_data[authorization]["model"].data


@app.get("/data/length")
def get_length_data(authorization: str = Header(...)):
    if authorization not in session_data:
        raise HTTPException(status_code=401, detail="Invalid session")

    update_session_activity(authorization)
    return len(session_data[authorization]["model"].data)

@app.post("/data/file")
def load_data_from_file(file: UploadFile = File(...), authorization: str = Header(...)):
    if authorization not in session_data:
        raise HTTPException(status_code=401, detail="Invalid session")

    text_file = io.TextIOWrapper(file.file, encoding="utf-8")
    try:
        session_data[authorization]["model"].load_data(text_file)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    update_session_activity(authorization)
    return session_data[authorization]["model"].data

@app.get("/data/file")
def get_file_from_data(background_tasks: BackgroundTasks, authorization: str = Header(...)):
    if authorization not in session_data:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        session_data[authorization]["model"].export_data("temporary_excel.xlsx")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при экспорте данных: {e}")

    background_tasks.add_task(lambda path: os.remove(path), "temporary_excel.xlsx")
    update_session_activity(authorization)

    return FileResponse(
        path="temporary_excel.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="Отчет_инвентаризации.xlsx"
    )

