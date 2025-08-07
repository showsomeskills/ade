import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import importlib
import glob

load_dotenv()

TOKEN = os.getenv('TOKEN')
DEFAULT_PREFIX = os.getenv('PREFIX', '-')  # fallback to '.' if PREFIX not set

intents = discord.Intents.default()
intents.message_content = True  # allows reading message content
intents.members = True          # crucial for member-related commands

def prefix_check(bot, message):
    prefixes = [DEFAULT_PREFIX]

    # Check if message starts with any known prefix
    for p in prefixes:
        if message.content.startswith(p):
            return p

    # If no prefix: check if first word matches a command name
    first_word = message.content.split(' ')[0].lower()
    if first_word in bot.all_commands:
        return ''  # empty prefix to allow no prefix command trigger

    # Else fallback to default mention prefix
    return commands.when_mentioned(bot, message)

bot = commands.Bot(command_prefix=prefix_check, intents=intents)

# Remove default help command to load your custom help command without conflict
bot.remove_command('help')

# Dynamically load command modules from commands folder
for file in glob.glob('./commands/*.py'):
    cmd_name = file[11:-3]  # strip './commands/' and '.py'
    module = importlib.import_module(f'commands.{cmd_name}')
    if hasattr(module, 'setup'):
        module.setup(bot)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("**Unknown command.** Type **.help** to see commands.", delete_after=5)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("**You don't have permission to use this command.**", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("**Missing arguments for this command.**", delete_after=5)
    else:
        await ctx.send(f"An error occurred: **{str(error)}**", delete_after=5)
        raise error  # re-raise to help with debugging if needed

bot.run(TOKEN)
