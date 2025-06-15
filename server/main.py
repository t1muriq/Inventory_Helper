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
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from data_base.converters import put_model_to_db, get_model_from_db, get_all_it_numbers
from application.model import Model, FileReader, ExcelExporter


# ----------- background tasks -----------

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

# ----------- definations of variables -----------

app = FastAPI(lifespan=lifespan)
session_data: Dict[str, Dict[str, Model | datetime]] = dict()
root_key = "1221"

# ----------- definations data base -----------

DATABASE_URL = "postgresql://postgres:123@localhost:5435/inventory_db"
engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
CurrentSession = SessionLocal()

# ----------- decorators -----------

def admin_required(expected_key: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, master_key: str = Header(...), **kwargs):
            if master_key != expected_key:
                raise HTTPException(status_code=403, detail="Forbidden: Invalid master key")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def session_required(data_dict: dict):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, authorization: str = Header(...), **kwargs):
            if authorization not in data_dict:
                raise HTTPException(status_code=401, detail="Invalid session")

            update_session_activity(authorization)
            return func(*args, authorization=authorization,**kwargs)
        return wrapper
    return decorator

# ----------- functools -----------

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

# ----------- root endpoints DELETE IN FUTURE -----------

@app.get("/root/session")
@admin_required(root_key)
def get_all_sessions(master_key: str = Header(...)):
    return session_data

@app.get("/root/time")
@admin_required(root_key)
def get_time_all_sessions(master_key: str = Header(...)):
    return [f"До конца сессии {session[0]} осталось {timedelta(minutes=5) - (datetime.now() - session[-1]["last_activity"])}" for session in session_data.items()]

@app.delete("/root/close")
@admin_required(root_key)
def close_session_root(master_key: str = Header(...), session_id: str = Query(...)):
    session_data.pop(session_id, None)
    return {"message": f"Session: {session_id} has been deleted"}

# ------------ normal endpoints ------------

@app.post("/session/create")
def create_session():
    session_id = generate_unique_session()
    session_data[session_id] = {
        "model": get_new_model(),
        "last_activity": datetime.now()
    }
    return {"session_id": session_id}

@app.delete("/session/close")
@session_required(session_data)
def close_session(authorization: str = Header(...)):

    session_data.pop(authorization, None)
    return {"message": f"Session: {authorization} close successfully"}

@app.get("/session/data")
@session_required(session_data)
def get_data(authorization: str = Header(...)):
    return session_data[authorization]["model"].data

@app.delete("/session/data")
@session_required(session_data)
def clear_data(authorization: str = Header(...)):
    session_data[authorization]["model"].clear_data()
    return {"message": "Data has been deleted successfully"}

@app.delete("/session/data/{item_id}")
@session_required(session_data)
def delete_elem_from_data(item_id: int, authorization: str = Header(...)):
    return f"Delete field: {item_id} Data: {session_data[authorization]["model"].data.pop(item_id)}"

@app.get("/session/data/length")
@session_required(session_data)
def get_length_data(authorization: str = Header(...)):
    return len(session_data[authorization]["model"].data)

@app.post("/session/data/upload-from-cloud")
@session_required(session_data)
def upload_data_from_cloud(authorization: str = Header(...)):
    it_nums = get_all_it_numbers(CurrentSession)
    for num in it_nums:
        session_data[authorization]["model"].load_data_from_model(get_model_from_db(CurrentSession, num), "cloud")
    return it_nums

@app.post("/session/data/download-to-cloud")
@session_required(session_data)
def download_data_to_cloud(authorization: str = Header(...)):
    ret = []
    for model in session_data[authorization]["model"].data:
        put_model_to_db(CurrentSession, model.system_data)
        ret.append(model.system_data.PC.Assigned_IT_Number)
    return ret

@app.post("/session/data/file")
@session_required(session_data)
def load_data_from_file(file: UploadFile = File(...), authorization: str = Header(...)):
    text_file = io.TextIOWrapper(file.file, encoding="utf-8")
    try:
        ret = session_data[authorization]["model"].load_data_from_file(text_file, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {"it_num": ret}

@app.get("/session/data/file")
@session_required(session_data)
def get_file_from_data(background_tasks: BackgroundTasks, authorization: str = Header(...)):
    try:
        session_data[authorization]["model"].export_data("temporary_excel.xlsx")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при экспорте данных: {e}")

    background_tasks.add_task(lambda path: os.remove(path), "temporary_excel.xlsx")

    return FileResponse(
        path="temporary_excel.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="Отчет_инвентаризации.xlsx"
    )

