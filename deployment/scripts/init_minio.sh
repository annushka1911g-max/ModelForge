#!/bin/sh
set -e

echo "Configuring MinIO client..."
mc alias set local http://${MINIO_ENDPOINT:-minio:9000} ${MINIO_ROOT_USER:-minio_admin} ${MINIO_ROOT_PASSWORD:-minio_secure_admin_password_placeholder}

echo "Creating buckets..."
mc mb --ignore-existing local/${MINIO_BUCKET_MODELS:-models}
mc mb --ignore-existing local/${MINIO_BUCKET_BATCH:-batch-jobs}

echo "MinIO buckets successfully initialized."
