# Build from root directory
# docker build -t myapp -f docker/Dockerfile .

"""
Stopped trying to containerize with Docker due to the size of the dependencies making it 
take too long to build and test the Docker image.
"""

# Use a base Python image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY docker/requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python files to the container
COPY app /app

# Set the entry point for the container
ENTRYPOINT ["python", "askPDF.py"]
