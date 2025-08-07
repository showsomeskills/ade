import discord
from discord.ext import commands
from difflib import get_close_matches

@commands.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, user_arg=None, *, reason=None):
    if user_arg is None:
        await ctx.send("Please specify a user to kick. Usage: .kick <user> [reason]", delete_after=3)
        return

    guild = ctx.guild

    def find_member(search):
        member = None
        # Mention
        if search.startswith('<@') and search.endswith('>'):
            try:
                user_id = int(search.strip('<@!>'))
                member = guild.get_member(user_id)
            except:
                pass
        # ID
        if not member and search.isdigit():
            member = guild.get_member(int(search))
        # Fuzzy search on names and display names
        if not member:
            names = [m.name for m in guild.members] + [m.display_name for m in guild.members]
            close_names = get_close_matches(search.lower(), [n.lower() for n in names], n=1, cutoff=0.5)
            if close_names:
                for m in guild.members:
                    if close_names[0] == m.name.lower() or close_names[0] == m.display_name.lower():
                        member = m
                        break
        return member

    member = find_member(user_arg)
    if not member:
        await ctx.send(f"Could not find a user matching **{user_arg}**.", delete_after=3)
        return

    if member == ctx.author:
        await ctx.send("You cannot kick yourself.", delete_after=3)
        return

    if member == guild.owner:
        await ctx.send("I cannot kick the server owner.", delete_after=3)
        return

    if member.top_role >= guild.me.top_role:
        await ctx.send("I cannot kick this user because their highest role is equal or higher than mine.", delete_after=3)
        return

    try:
        if reason:
            try:
                dm_message = f"You have been kicked from **{guild.name}** for the following reason:\n{reason}"
                await member.send(dm_message)
            except discord.Forbidden:
                # User DMs closed or blocked bot, silently pass
                pass

        await member.kick(reason=reason)

        if reason:
            await ctx.send(f"Kicked **{member.display_name}** for reason: {reason}")
        else:
            await ctx.send(f"Kicked **{member.display_name}**.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to kick that user.", delete_after=3)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to kick user. Error: **{e}**", delete_after=3)

def setup(bot):
    bot.add_command(kick)
