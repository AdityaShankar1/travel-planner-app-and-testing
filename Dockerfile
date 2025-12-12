# Use official Python image
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose ports: FastAPI (8000) and Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# Start both FastAPI and Streamlit
CMD uvicorn main5:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app.py --server.port 8501 --server.headless true
