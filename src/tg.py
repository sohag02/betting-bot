from telethon import TelegramClient
import asyncio
from src.config import get_config

config = get_config()

client = TelegramClient(
    api_id=config.telegram.api_id,
    api_hash=config.telegram.api_hash,
    session='bot'
)

async def send(msg: str):
    await client.start(bot_token=config.telegram.bot_token)
    await client.send_message(config.telegram.admin_username, msg)

def notify(msg: str):
    asyncio.run(send(msg))

if __name__ == "__main__":
    notify("test")