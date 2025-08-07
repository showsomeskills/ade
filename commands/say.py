from discord.ext import commands

@commands.command(name='say')
@commands.has_permissions(manage_messages=True)  # Optional: restrict to users with manage_messages permission
async def say(ctx, *, msg: str = None):
    """
    Bot repeats exactly what you say.

    Usage:
    .say <text>
    """
    if not msg:
        await ctx.send("**Please provide a message to say.**", delete_after=5)
        return

    # Delete the command message to keep chat clean
    try:
        await ctx.message.delete()
    except:
        pass  # Ignore if bot can't delete the user's message

    # Send the exact text
    await ctx.send(msg)

def setup(bot):
    bot.add_command(say)
