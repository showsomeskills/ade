import discord
from discord.ext import commands
import random

@commands.command(name='purge')
@commands.has_permissions(manage_messages=True)
async def purge(ctx, target: str = None, amount: str = None):
    """Purge messages.
    
    Usage:
    .purge <amount>                - deletes <amount> recent messages
    .purge <user> <amount>         - deletes <amount> recent messages from that user
    """

    if target is None:
        await ctx.send("Please specify the number of messages to delete (1-100), or a user and number.", delete_after=5)
        return

    # Case 1: only one argument, treat as amount to purge from everyone
    if amount is None:
        amount = target
        try:
            number = int(amount)
            if number < 1 or number > 100:
                await ctx.send("Please provide a number between 1 and 100.", delete_after=5)
                return
            # +1 to include command message
            deleted = await ctx.channel.purge(limit=number + 1)
            count = len(deleted) - 1
            replies = [
                f"Removed **{count}** messages as you asked.",
                f"Purged **{count}** messages successfully.",
            ]
            await ctx.send(random.choice(replies), delete_after=5)
        except ValueError:
            await ctx.send("That doesn't look like a valid number. Please enter a number between 1 and 100.", delete_after=5)
        return

    # Case 2: two arguments: purge number of messages from a specific user

    user_arg = target
    number_arg = amount

    # Find member helper
    def find_member(search):
        member = None
        # Mention
        if search.startswith('<@') and search.endswith('>'):
            try:
                user_id = int(search.strip('<@!>'))
                member = ctx.guild.get_member(user_id)
            except:
                pass
        # ID
        if not member and search.isdigit():
            member = ctx.guild.get_member(int(search))
        # Username#discriminator exact match
        if not member and '#' in search:
            name, disc = search.split('#', 1)
            for m in ctx.guild.members:
                if m.name == name and m.discriminator == disc:
                    member = m
                    break
        # Fuzzy name/display_name match
        if not member:
            names = [m.name for m in ctx.guild.members] + [m.display_name for m in ctx.guild.members]
            close = [n for n in names if search.lower() in n.lower()]
            if close:
                for m in ctx.guild.members:
                    if m.name.lower() in close or m.display_name.lower() in close:
                        return m
        return member

    member = find_member(user_arg)
    if not member:
        await ctx.send(f"Could not find a user matching **{user_arg}**.", delete_after=5)
        return

    try:
        number = int(number_arg)
        if number < 1 or number > 100:
            await ctx.send("Please provide a number between 1 and 100 for messages to purge.", delete_after=5)
            return
    except ValueError:
        await ctx.send("That doesn't look like a valid number. Please enter a number between 1 and 100.", delete_after=5)
        return

    def is_target_user(m):
        return m.author == member or (m.author.bot and member.bot)  # include bots if user is bot

    # Fetch limit (to avoid scanning tons of messages)
    fetch_limit = 500  # search last 500 messages max

    deleted_messages = []
    try:
        async for message in ctx.channel.history(limit=fetch_limit):
            if message.author == member:
                deleted_messages.append(message)
                if len(deleted_messages) >= number:
                    break

        if not deleted_messages:
            await ctx.send(f"No messages found from **{member.display_name}** to delete.", delete_after=5)
            return

        # Bulk delete
        await ctx.channel.delete_messages(deleted_messages)
        await ctx.send(f"Removed **{len(deleted_messages)}** messages from **{member.display_name}**.", delete_after=5)

    except discord.Forbidden:
        await ctx.send("I don't have permission to delete messages.", delete_after=5)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to delete messages: **{e}**", delete_after=5)

def setup(bot):
    bot.add_command(purge)
