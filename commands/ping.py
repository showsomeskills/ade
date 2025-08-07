import discord
from discord.ext import commands

@commands.command(name='ping')
async def ping(ctx):
    latency_ms = round(ctx.bot.latency * 1000)
    await ctx.send(f"Pong! Bot latency is **{latency_ms}ms**.")

def setup(bot):
    bot.add_command(ping)
