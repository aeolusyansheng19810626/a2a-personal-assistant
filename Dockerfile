FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create .env file with DEMO_MODE enabled
RUN echo "GROQ_API_KEY=${GROQ_API_KEY}" > .env && \
    echo "DEMO_MODE=true" >> .env

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose Streamlit port (HuggingFace Spaces requirement)
EXPOSE 7860

# Create log directory
RUN mkdir -p /var/log/supervisor

# Start supervisor to manage all services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

# Made with Bob
