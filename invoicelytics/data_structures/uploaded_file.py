from dataclasses import dataclass


@dataclass
class UploadedFile:
    filename: str
    contents: bytes
    content_type: str

    def read(self):
        return self.contents
