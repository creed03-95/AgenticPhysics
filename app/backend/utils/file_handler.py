import os
from fastapi import UploadFile
from pathlib import Path
import shutil

class FileHandler:
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    async def save_upload_file(self, upload_file: UploadFile) -> str:
        """
        Save uploaded file and return the path
        """
        file_path = self.upload_dir / upload_file.filename
        
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
        finally:
            upload_file.file.close()
        
        return str(file_path)
    
    def cleanup_file(self, file_path: str):
        """
        Clean up temporary files
        """
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {str(e)}") 