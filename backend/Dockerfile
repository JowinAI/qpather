FROM python:3.9

# Set working directory
WORKDIR /code

# Install system dependencies for ODBC and pyodbc
RUN apt-get update && \
    apt-get install -y \
    unixodbc-dev \
    curl \
    gnupg && \
    # Add Microsoft package signing key directly to trusted.gpg.d
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-archive-keyring.gpg && \
    # Add the Microsoft SQL Server repository manually (replace "buster" with your Debian version if different)
    echo "deb [signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/debian/10/prod buster main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    apt-get clean

# Install Python dependencies
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application code
COPY . /code

# Start FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082", "--reload"]
