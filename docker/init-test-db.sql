SELECT 'CREATE DATABASE fastapi_microservice_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'fastapi_microservice_test')\gexec
