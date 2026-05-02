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

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose Streamlit port (HuggingFace Spaces requirement)
EXPOSE 7860

# Create log directory
RUN mkdir -p /var/log/supervisor

# Create startup script
RUN printf '#!/bin/bash\n\
set -e\n\
\n\
# Create .env file with runtime environment variables\n\
echo "GROQ_API_KEY=${GROQ_API_KEY}" > /app/.env\n\
echo "DEMO_MODE=true" >> /app/.env\n\
\n\
echo "Starting services..."\n\
echo "GROQ_API_KEY is set: $([ -n "${GROQ_API_KEY}" ] && echo "YES" || echo "NO")"\n\
\n\
# Start supervisor in foreground\n\
exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf\n\
' > /start.sh && chmod +x /start.sh

# Start with the startup script
CMD ["/start.sh"]

# Made with Bob
