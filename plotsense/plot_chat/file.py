from io import BytesIO
from openai.types import FilePurpose


class FileClient:
    def __init__(self, client):
        self.client = client

    def upload_file(self, file_obj: BytesIO, purpose: FilePurpose) -> str:
        response = self.client.files.create(file=file_obj, purpose=purpose)
        return response.id

    def delete_file(self, file_id: str):
        self.client.files.delete(file_id)

