import discord
from discord.ext import commands
from difflib import get_close_matches

@commands.command(name='nick')
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, user_arg=None, *, new_nick=None):
    if not user_arg:
        await ctx.send("Usage: .nick <user> [new_nickname]\nIf no new nickname is provided, clears the user's nickname.", delete_after=5)
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
        # Username#discriminator exact match
        if not member and '#' in search:
            name, disc = search.split('#', 1)
            for m in guild.members:
                if m.name == name and m.discriminator == disc:
                    member = m
                    break
        # Fuzzy name/display_name match
        if not member:
            names = [m.name for m in guild.members] + [m.display_name for m in guild.members]
            close = get_close_matches(search.lower(), [n.lower() for n in names], n=1, cutoff=0.5)
            if close:
                for m in guild.members:
                    if close[0] == m.name.lower() or close[0] == m.display_name.lower():
                        member = m
                        break
        return member

    member = find_member(user_arg)
    if not member:
        await ctx.send(f"Could not find a user matching **{user_arg}**.", delete_after=3)
        return

    # Permission checks for hierarchy
    if member == guild.owner:
        await ctx.send("Cannot change the nickname of the server owner.", delete_after=3)
        return

    if member.top_role >= guild.me.top_role:
        await ctx.send("I cannot change the nickname of a user with an equal or higher role than mine.", delete_after=3)
        return

    try:
        # If no new nickname given -> clear current nickname
        if new_nick is None:
            if member.nick is None:
                await ctx.send(f"**{member.display_name}** does not have a nickname set.", delete_after=3)
                return
            await member.edit(nick=None, reason=f"Nickname cleared by {ctx.author}")
            await ctx.send(f"Cleared nickname for **{member.name}**.")
            return

        # If new nickname is the same as their original username -> clear nick instead
        if new_nick.strip() == member.name:
            if member.nick is None:
                await ctx.send(f"**{member.display_name}**'s nickname is already their username.", delete_after=3)
                return
            await member.edit(nick=None, reason=f"Nickname cleared by {ctx.author} (new nick same as username)")
            await ctx.send(f"Changed nickname for **{member.name}** to their original username (cleared nickname).")
            return

        # Otherwise, set new nickname
        await member.edit(nick=new_nick, reason=f"Nickname changed by {ctx.author}")
        await ctx.send(f"Changed nickname for **{member.name}** to **{new_nick}**.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to change this user's nickname.", delete_after=3)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to change nickname. Error: **{e}**", delete_after=3)

def setup(bot):
    bot.add_command(nick)
