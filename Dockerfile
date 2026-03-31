# Use a lightweight version of Python
FROM python:3.11-slim

# Create a folder for our app
WORKDIR /app

# Install the required tools
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all our code into the cloud
COPY . .

# Open the port that Fly.io likes to use
EXPOSE 8080

# The command to wake Dumbo up!
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8080"]