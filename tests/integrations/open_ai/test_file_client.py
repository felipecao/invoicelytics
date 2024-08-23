from unittest import TestCase
from unittest.mock import MagicMock

from openai.types import FileObject

from invoicelytics.data_structures.uploaded_file import UploadedFile
from invoicelytics.integrations.open_ai.file_client import FileClient
from tests import test_faker


class TestFileClient(TestCase):

    def setUp(self):
        self.mock_create = MagicMock()
        self.mock_client = MagicMock()
        self.mock_client.files.create = self.mock_create

        self.file_client = FileClient(client=self.mock_client)

    def test_upload_file(self):
        filename = test_faker.file_name(extension=".pdf")
        content = b"file contents"
        file_type = "application/pdf"
        file_id = test_faker.ssn()

        uploaded_file = UploadedFile(filename, content, file_type)
        payload = MagicMock(spec=FileObject)
        payload.id = file_id
        self.mock_create.return_value = payload

        result = self.file_client.upload_file(uploaded_file)

        self.assertEqual(result, file_id)
        self.mock_create.assert_called_once_with(file=(filename, content, file_type), purpose="assistants")
