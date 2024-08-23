import os
import shutil

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


class UploadFolder:
    @staticmethod
    def save_to_filesystem(uploaded_file: FileStorage):
        file_name = secure_filename(uploaded_file.filename)
        file_path = os.path.join(os.environ["UPLOAD_FOLDER"], file_name)

        uploaded_file.save(file_path)
        return file_path

    @staticmethod
    def move_file(old_file_path: str, new_file_path: str):
        new_directory = os.path.dirname(new_file_path)
        os.makedirs(new_directory, exist_ok=True)
        shutil.move(old_file_path, new_file_path)

    @staticmethod
    def read_file(path: str) -> bytes:
        with open(path, "rb") as file:
            return file.read()
