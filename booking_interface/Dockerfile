# Use the official Python 3.11 slim image as the base image
FROM python:3.11.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install the Python dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire contents of the booking_system folder into the container
COPY . /app/

# Expose the port that Streamlit uses (default is 8501)
EXPOSE 8502

# Set the command to run the Streamlit application
CMD ["streamlit", "run", "booking_interface.py", "--server.port=8502", "--server.address=0.0.0.0"]
