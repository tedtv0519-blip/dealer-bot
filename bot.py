import os

TOKEN = os.getenv("BOT_TOKEN")

print("Bot token loaded:", TOKEN is not None)
