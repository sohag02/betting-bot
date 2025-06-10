FROM selenium/standalone-chrome:latest

USER root

# Install git and other necessary build tools
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    pip install --upgrade pip

# Set working directory
WORKDIR /home/seluser/scripts

# Copy your files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start your bot instead of Selenium Grid
CMD ["sh", "-c", "python main.py && python run_ui.py"]