import os
import uuid
from fastapi import UploadFile

def save_uploaded_file(upload_file: UploadFile, upload_dir: str = "uploads") -> str:
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(upload_file.filename)[1]
    
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, unique_name)

    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())

    return file_path

def delete_uploaded_file(file: str = None, multiple_file: list[str] = None):
    if file and os.path.exists(file):
        os.remove(file)

    if multiple_file:
        for f in multiple_file:
            path = os.path.normpath(f)
            if os.path.exists(path):
                os.remove(path)

    return ""