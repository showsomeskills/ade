import discord
from discord.ext import commands
from difflib import get_close_matches

@commands.command(name='unlock')
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, *, channel_arg=None):
    guild = ctx.guild

    def find_channel(search):
        if not search:
            return None

        channel = None

        # Mention (like <#channel_id>)
        if search.startswith('<#') and search.endswith('>'):
            try:
                channel_id = int(search.strip('<#>'))
                channel = guild.get_channel(channel_id)
            except:
                pass

        # ID only
        if not channel and search.isdigit():
            channel = guild.get_channel(int(search))

        # Fuzzy name search among text channels
        if not channel:
            text_channels = [c for c in guild.channels if isinstance(c, discord.TextChannel)]
            names = [c.name for c in text_channels]
            close_matches = get_close_matches(search.lower(), [name.lower() for name in names], n=1, cutoff=0.5)
            if close_matches:
                for c in text_channels:
                    if c.name.lower() == close_matches[0]:
                        channel = c
                        break

        return channel

    channel = find_channel(channel_arg) if channel_arg else ctx.channel
    if not channel:
        await ctx.send(f"Could not find a text channel matching **{channel_arg}**.", delete_after=3)
        return

    everyone = guild.default_role
    overwrite = channel.overwrites_for(everyone)
    overwrite.send_messages = None  # Resets to default (unlocked)

    try:
        await channel.set_permissions(everyone, overwrite=overwrite, reason=f"Unlocked by {ctx.author}")
        await ctx.send(f"Channel **{channel.name}** is now unlocked.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to modify channel permissions.", delete_after=3)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to unlock the channel. Error: **{e}**", delete_after=3)

def setup(bot):
    bot.add_command(unlock)
