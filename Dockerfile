# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /app/venv

# Activate the virtual environment and install dependencies
# Note: Use the full path to the venv `pip` to ensure it installs within the venv
COPY requirements.txt .
RUN pip install streamlit
RUN /app/venv/bin/pip --version
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port (if using a web app like Flask/Streamlit)
EXPOSE 8501

# Define the default command
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
