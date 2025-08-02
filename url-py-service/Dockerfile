# # Use a slim Python 3.9 image
# FROM python:3.9-slim

# # Set Work Directory
# WORKDIR /app

# # Install Dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy App Code
# COPY . .

# # Expose the Port for the Application
# EXPOSE 5000

# # Command to Run the App with Gunicorn
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.main:app"]

# ==================================================xxxxxxxxxxxxxxxxxxxxxxxxxx=========================
# ==================================================xxxxxxxxxxxxxxxxxxxxxxxxxx=========================


# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for psycopg2 and other requirements
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port for the app
EXPOSE 5000

# Use Gunicorn for production server
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]



# Use Gunicorn with eventlet for production server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--worker-class", "eventlet", "-w", "1", "app:app"]


# ==================================================xxxxxxxxxxxxxxxxxxxxxxxxxx=========================
# ==================================================xxxxxxxxxxxxxxxxxxxxxxxxxx=========================