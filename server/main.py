import os
from typing import List

from application.model import Model, FileReader, ExcelExporter
from application.model import IReader

from fastapi import FastAPI, File, UploadFile, Query, BackgroundTasks
from fastapi.responses import FileResponse

class FastApiReader(IReader):
    def read_data(self, file: List[File]) -> List[str]:
        pass

app = FastAPI()
model = Model(FileReader(), ExcelExporter())

@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}

@app.post("/data")
def load_data(UploadFile = File(...)):
    files = ... # Лист путей на файлы

    if files:
        # model.clear_data()
        for file in files:
            try:
                model.load_data(file)
            except Exception as e:
                print(e)

