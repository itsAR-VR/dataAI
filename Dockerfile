# Use an official Python runtime as the parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Install PostgreSQL client
RUN apt-get update && apt-get install -y libpq-dev

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Copy the current directory contents into the container at /app
COPY . .

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Use CMD to specify the default command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]