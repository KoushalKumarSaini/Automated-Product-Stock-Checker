# Use an official Python runtime as a parent image.
# This image includes a full Debian OS, Python, and the necessary tools.
FROM python:3.9-slim-buster

# Prevent Python from writing .pyc files to disc and buffering stdout.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies needed by undetected-chromedriver and for installing Python packages.
# The undetected_chromedriver library needs a Chrome installation to work.
RUN apt-get update \
    && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container and install dependencies.
# This step is done separately to leverage Docker's caching, so it only re-installs
# dependencies if requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's source code into the container.
COPY . .

# Set the entry point for the container. This command will be executed when
# the container starts. The -u flag ensures output is not buffered.
CMD ["python", "-u", "check_stock.py"]
