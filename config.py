import os
from tortoise import Tortoise
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk import WebClient

SCHEDULER_USER = os.getenv("SCHEDULER_USER")
PYTHONPATH = os.getenv("PYTHONPATH")
DATABASE_URL = os.getenv("DATABASE_URL")
LOG_FILE = os.getenv("LOG_FILE")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "debezium_wrapper": {
            "models": ["data.db.models", 'aerich.models'],
            "default_connection": "default",
        }
    }
}

slack_client = AsyncWebClient(token=SLACK_BOT_TOKEN)
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')
