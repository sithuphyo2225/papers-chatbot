# Use the official Python image as a base
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies for building SQLite
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install SQLite by specifying the exact download link
RUN wget https://www.sqlite.org/2023/sqlite-autoconf-3430100.tar.gz && \
    tar xzvf sqlite-autoconf-3430100.tar.gz && \
    cd sqlite-autoconf-3430100 && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf sqlite-autoconf-3430100*


# Verify the updated SQLite version
RUN sqlite3 --version

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
