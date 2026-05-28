# ---------------------------------------
# STAGE 1: Build Svelte Frontend
# ---------------------------------------
FROM node:22 AS frontend-builder

WORKDIR /app/frontend

# Copy frontend config and install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source code and build it
COPY frontend/ ./
RUN npm run build

# ---------------------------------------
# STAGE 2: Setup FastAPI Backend
# ---------------------------------------
FROM python:3.10-slim

WORKDIR /app/backend

# Install required system packages
RUN apt-get update && apt-get install -y gcc

# Copy python requirements and install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./

# Copy the built Svelte frontend from Stage 1 into backend/static
COPY --from=frontend-builder /app/frontend/dist /app/backend/static

# Hugging Face Spaces requires port 7860
EXPOSE 7860

# Run Uvicorn on 0.0.0.0 and port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]