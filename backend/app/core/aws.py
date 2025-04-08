import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AWSClient:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.AWS_BUCKET_NAME

    async def upload_file(self, file_obj, file_name: str, content_type: str = None) -> str:
        """
        Upload a file to S3 bucket
        """
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                file_name,
                ExtraArgs=extra_args
            )

            # Generate the URL for the uploaded file
            url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_name}"
            return url

        except ClientError as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            raise HTTPException(status_code=500, detail="Error uploading file to storage")

    async def delete_file(self, file_name: str) -> bool:
        """
        Delete a file from S3 bucket
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_name
            )
            return True

        except ClientError as e:
            logger.error(f"Error deleting file from S3: {str(e)}")
            raise HTTPException(status_code=500, detail="Error deleting file from storage")

    async def get_file_url(self, file_name: str, expiration: int = 3600) -> str:
        """
        Generate a pre-signed URL for temporary access to a file
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_name
                },
                ExpiresIn=expiration
            )
            return url

        except ClientError as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise HTTPException(status_code=500, detail="Error generating file access URL")

# Create a singleton instance
aws_client = AWSClient() 