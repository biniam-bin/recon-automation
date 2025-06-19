import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT')
}

# Slack configuration
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

# Other settings
TEMP_DIR = '/tmp/recon'