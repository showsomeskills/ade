import discord
from discord.ext import commands
import asyncio

@commands.command(name='nuke')
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    await ctx.send("**Are you sure?**")

    def check(m):
        return (
            m.author == ctx.author and
            m.channel == ctx.channel and
            m.content.lower() in [
                "y", "yess", "yes", "ye", "yep", "yepp",
                "n", "no", "nop", "nope"
            ]
        )

    try:
        msg = await ctx.bot.wait_for('message', check=check, timeout=30.0)
    except asyncio.TimeoutError:
        await ctx.send("Nuke cancelled.", delete_after=5)
        return

    response = msg.content.lower()
    if response in ["y", "yess", "yes", "ye", "yep", "yepp"]:
        channel = ctx.channel
        try:
            name = channel.name
            category = channel.category
            position = channel.position
            overwrites = channel.overwrites
            topic = getattr(channel, "topic", None)
            nsfw = getattr(channel, "nsfw", False)
            slowmode_delay = getattr(channel, "slowmode_delay", 0)
            guild = ctx.guild

            # Delete the original channel first
            await channel.delete(reason=f"Nuked by {ctx.author}")

            # Create the new channel (appears at the bottom at first)
            new_channel = await guild.create_text_channel(
                name=name,
                category=category,
                overwrites=overwrites,
                topic=topic,
                nsfw=nsfw,
                slowmode_delay=slowmode_delay,
                reason=f"Nuked by {ctx.author}"
            )

            # Move the new channel to the original position
            await new_channel.edit(position=position)

            await new_channel.send("**Nuked.**")
        except discord.Forbidden:
            # We can't send a message in the old channel since it's deleted, so use DM on error
            await ctx.author.send("I don't have permission to nuke (manage channels).")
        except Exception as e:
            try:
                await ctx.author.send(f"Failed to nuke channel. Error: **{e}**")
            except:
                pass
    else:
        await ctx.send("Nuke cancelled.", delete_after=5)

def setup(bot):
    bot.add_command(nuke)
