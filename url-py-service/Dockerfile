# Use Python Slim as Base Image
FROM python:3.9-slim

# Set Work Directory
WORKDIR /app

# Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy App Code
COPY . .

# Expose Port
EXPOSE 5000

# Command to Run the App
CMD ["python", "app.py"]
