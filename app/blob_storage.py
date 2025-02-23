import os
from uuid import uuid4
from app.exceptions import BlobStorageError


class MockBlobStorageService:
    """Mock service for testing"""

    def __init__(self):
        """Mock init that doesn't need connection string"""
        pass  # No need to initialize anything for mock

    def upload_image(self, image_data, content_type):
        """Mock upload that returns a consistent URL"""
        return (
            "https://maisonblobstorage.blob.core.windows.net/"
            "property-images/test-image.jpg"
        )

    def delete_image(self, image_url):
        """Mock delete that does nothing"""
        pass


try:
    from azure.storage.blob import BlobServiceClient

    class BlobStorageService:
        def __init__(self):
            connection_string = os.environ.get(
                "AZURE_STORAGE_CONNECTION_STRING"
            )
            if not connection_string:
                raise ValueError("Azure Storage connection string not set")
            self.blob_service_client = (
                BlobServiceClient.from_connection_string(connection_string)
            )
            self.container_name = "property-images"

        def upload_image(self, image_data, content_type):
            """Upload image to blob storage and return URL"""
            try:
                # Create container if it doesn't exist
                container_client = (
                    self.blob_service_client.get_container_client(
                        self.container_name
                    )
                )
                if not container_client.exists():
                    container_client.create_container(public_access="blob")

                # Generate unique blob name
                blob_name = f"{uuid4()}.jpg"
                blob_client = container_client.get_blob_client(blob_name)

                # Upload the image
                blob_client.upload_blob(
                    image_data,
                    blob_type="BlockBlob",
                    content_type=content_type,
                    overwrite=True,
                )

                # Return the URL
                return blob_client.url

            except Exception as e:
                print(f"Error in upload_image: {str(e)}")
                raise Exception(
                    f"Failed to upload image to blob storage: {str(e)}"
                )

        def delete_image(self, image_url):
            """Delete image from blob storage"""
            try:
                # Extract blob name from URL
                blob_name = image_url.split("/")[-1]

                # Get blob client
                container_client = (
                    self.blob_service_client.get_container_client(
                        self.container_name
                    )
                )
                blob_client = container_client.get_blob_client(blob_name)

                # Delete the blob
                blob_client.delete_blob()

            except Exception as e:
                raise BlobStorageError(f"Failed to delete image: {str(e)}")

except ImportError:
    BlobStorageService = MockBlobStorageService
