import os
import tempfile
import shutil
import asyncio
from unittest import TestCase
from unittest.mock import patch, MagicMock
from uuid import uuid4

from invoicelytics.temporal.activity.filesystem import move_invoice_to_tenant_folder, _generate_new_file_path
from invoicelytics.temporal.parameters import InvoiceInferenceWorkflowParams
from tests import test_faker


class TestFilesystemActivity(TestCase):
    def setUp(self):
        self._invoice_id = uuid4()
        self._tenant_id = uuid4()
        self._uploader_id = uuid4()
        self._file_path = test_faker.file_path()

        self.params = InvoiceInferenceWorkflowParams(
            invoice_id=self._invoice_id, tenant_id=self._tenant_id, uploader_id=self._uploader_id, file_path=self._file_path
        )

        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.original_upload_folder = os.environ.get("UPLOAD_FOLDER")
        os.environ["UPLOAD_FOLDER"] = self.temp_dir

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

        # Restore original environment variable
        if self.original_upload_folder:
            os.environ["UPLOAD_FOLDER"] = self.original_upload_folder
        elif "UPLOAD_FOLDER" in os.environ:
            del os.environ["UPLOAD_FOLDER"]

    @patch("invoicelytics.temporal.activity.filesystem.UploadFolder")
    def test_move_invoice_to_tenant_folder_success(self, mock_upload_folder):
        """Test successful execution of move_invoice_to_tenant_folder activity"""
        # Mock the UploadFolder.move_file method
        mock_upload_folder.move_file = MagicMock()

        # Execute the activity using asyncio
        result = asyncio.run(move_invoice_to_tenant_folder(self.params))

        # Verify the expected new file path
        expected_new_path = _generate_new_file_path(self._tenant_id, self._invoice_id)
        self.assertEqual(result, expected_new_path)

        # Verify UploadFolder.move_file was called with correct parameters
        mock_upload_folder.move_file.assert_called_once_with(self._file_path, expected_new_path)
