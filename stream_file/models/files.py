from pydantic import BaseModel
from fastapi import UploadFile,File,Form

class ItemFile(BaseModel):
    file:UploadFile=File(...)
    path:str=Form(...)
