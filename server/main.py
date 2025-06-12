import os
from typing import List, TextIO
import io

from application.model import Model, FileReader, ExcelExporter
from application.model import IReader

from fastapi import FastAPI, File, UploadFile, Query, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse


app = FastAPI()
model = Model(FileReader(), ExcelExporter())

@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}

@app.delete("/data")
def clear_data():
    model.clear_data()
    return {"message": "Data has been deleted successfully"}

@app.delete("/data/{item_id}")
def delete_elem_from_data(item_id: int):
    return f"Delete field: {item_id} Data: {model.data.pop(item_id)}"

@app.get("/data")
def get_data():
    return model.data

@app.post("/data")
def insert_data():
    pass

@app.get("/data/length")
def get_length_data():
    return len(model.data)

@app.post("/data/file")
def load_data_from_file(file: UploadFile = File(...)):
    text_file = io.TextIOWrapper(file.file, encoding="utf-8")
    try:
        model.load_data(text_file)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return model.data

@app.get("/data/file")
def get_file_from_data(background_tasks: BackgroundTasks):
    try:
        model.export_data("temporary_excel.xlsx")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при экспорте данных: {e}")

    background_tasks.add_task(lambda path: os.remove(path), "temporary_excel.xlsx")
    return FileResponse(
        path="temporary_excel.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="Отчет_инвентаризации.xlsx"
    )

