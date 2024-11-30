# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt /app/

# Install dependencies from requirements.txt
RUN apt-get update && apt-get install -y postgresql-client \
    && pip install --no-cache-dir -r requirements.txt && pip list

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port Streamlit will run on
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
