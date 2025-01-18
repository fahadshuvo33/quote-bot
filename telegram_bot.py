import os
import random
import requests
from datetime import datetime
import asyncio

# from dotenv import load_dotenv
# import discord
# from discord.ext import commands, tasks
# from telegram import Update
# from telegram.ext import Application, CommandHandler, ContextTypes

# # Load environment variables
# load_dotenv()

# # Configuration
# TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# QUOTES_API_KEY = os.getenv("QUOTES_API_KEY")  # If using a paid API


# class QuoteManager:
#     def __init__(self):
#         # Sample quotes for demonstration - you can replace with API calls
#         self.quotes = [
#             {
#                 "quote": "Be the change you wish to see in the world.",
#                 "author": "Mahatma Gandhi",
#             },
#             {
#                 "quote": "The only way to do great work is to love what you do.",
#                 "author": "Steve Jobs",
#             },
#             # Add more quotes here
#         ]

#     async def get_random_quote(self):
#         return await random.choice(self.quotes)

#     async def get_quote_from_api(self):
#         """
#         Example of fetching quote from an API
#         You can implement your preferred quote API here
#         """
#         try:
#             response = requests.get("https://api.quotable.io/random")
#             if response.status_code == 200:
#                 data = response.json()
#                 return {"quote": data["content"], "author": data["author"]}
#         except Exception as e:
#             print(f"Error fetching quote: {e}")
#         return self.get_random_quote()


# # Discord Bot Setup
# class DiscordQuoteBot(commands.Bot):
#     def __init__(self):
#         intents = discord.Intents.default()
#         intents.message_content = True
#         super().__init__(command_prefix="!", intents=intents)
#         self.quote_manager = QuoteManager()

#     async def setup_hook(self):
#         self.daily_quote.start()

#     @tasks.loop(hours=24)
#     async def daily_quote(self):
#         # Get the channel where you want to send daily quotes
#         channel = self.get_channel(int(os.getenv("DISCORD_CHANNEL_ID")))
#         if channel:
#             quote = await self.quote_manager.get_quote_from_api()
#             await channel.send(
#                 f"📜 Daily Quote:\n\"{quote['quote']}\"\n- {quote['author']}"
#             )

#     @commands.command(name="quote")
#     async def get_quote(self, ctx):
#         quote = await self.quote_manager.get_quote_from_api()
#         await ctx.send(f"📜 \"{quote['quote']}\"\n- {quote['author']}")


# # Telegram Bot Setup
# class TelegramQuoteBot:
#     def __init__(self):
#         self.quote_manager = QuoteManager()

#     async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
#         await update.message.reply_text(
#             "Welcome to the Daily Quote Bot! Use /quote to get a quote."
#         )

#     async def get_quote(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
#         quote = self.quote_manager.get_random_quote()
#         await update.message.reply_text(f"📜 \"{quote['quote']}\"\n- {quote['author']}")


# async def run_telegram_bot():
#     telegram_bot = TelegramQuoteBot()
#     application = Application.builder().token(TELEGRAM_TOKEN).build()

#     # Add command handlers
#     application.add_handler(CommandHandler("start", telegram_bot.start))
#     application.add_handler(CommandHandler("quote", telegram_bot.get_quote))

#     # Start the bot
#     await application.initialize()

#     # Start the bot
#     await application.start()
#     await application.updater.start_polling()

#     # Shutdown the bot
#     # await application.updater.stop()
#     # await application.stop()
#     # await application.shutdown()
#     await application.idle()


# async def main():
#     # Initialize Discord bot
#     discord_bot = DiscordQuoteBot()

#     # Run both bots concurrently
#     await asyncio.gather(discord_bot.start(DISCORD_TOKEN), run_telegram_bot())


# if __name__ == "__main__":
#     # asyncio.run(main())
#     asyncio.run(run_telegram_bot())


import os
import random
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import time

# Load environment variables
load_dotenv()


class QuoteManager:
    def __init__(self):
        # Expanded local quotes collection for better fallback
        self.quotes = [
            {
                "quote": "Be the change you wish to see in the world.",
                "author": "Mahatma Gandhi",
            },
            {
                "quote": "The only way to do great work is to love what you do.",
                "author": "Steve Jobs",
            },
            {
                "quote": "Life is what happens when you're busy making other plans.",
                "author": "John Lennon",
            },
            {
                "quote": "Success is not final, failure is not fatal.",
                "author": "Winston Churchill",
            },
            {
                "quote": "The future belongs to those who believe in the beauty of their dreams.",
                "author": "Eleanor Roosevelt",
            },
            {
                "quote": "Imagination is more important than knowledge.",
                "author": "Albert Einstein",
            },
            {
                "quote": "The best way to predict the future is to create it.",
                "author": "Peter Drucker",
            },
            {"quote": "Everything you can imagine is real.", "author": "Pablo Picasso"},
        ]
        self.last_api_attempt = 0
        self.api_cooldown = 60  # Wait 60 seconds before retrying API if it fails

    def get_random_quote(self):
        return random.choice(self.quotes)

    def get_quote_from_api(self):
        current_time = time.time()

        # Only try API if enough time has passed since last failure
        if current_time - self.last_api_attempt < self.api_cooldown:
            print("Using local quote due to recent API failure")
            return self.get_random_quote()

        try:
            api_key = os.getenv("API_NINJA_KEY")
            if not api_key:
                print("Error: API_NINJA_KEY not found in .env file")
                return self.get_random_quote()

            headers = {"X-Api-Key": api_key}
            response = requests.get(
                "https://api.api-ninjas.com/v1/quotes?category=inspirational",
                headers=headers,
                timeout=5,
            )

            if response.status_code == 200:
                data = response.json()
                if data:
                    quote_data = data[0]  # API Ninja returns a list of quotes
                    print("Successfully fetched quote from API Ninja")
                    return {
                        "quote": quote_data["quote"],
                        "author": quote_data.get("author", "Unknown"),
                    }
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {str(e)}")
            self.last_api_attempt = current_time
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            self.last_api_attempt = current_time

        print("Falling back to local quote")
        return self.get_random_quote()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Daily Quote Bot! 🎯\n\n"
        "Available commands:\n"
        "/quote - Get an inspiring quote\n"
        "/start - Show this help message"
    )


async def get_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote_manager = QuoteManager()
    quote = quote_manager.get_quote_from_api()
    await update.message.reply_text(
        f"📜 \"{quote['quote']}\"\n\n— {quote['author']} ✨"
    )


def main():
    # Create the application
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("Error: TELEGRAM_TOKEN not found in .env file")
        return

    print("Starting bot...")
    app = Application.builder().token(token).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quote", get_quote))

    # Run the bot until the user presses Ctrl-C
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
