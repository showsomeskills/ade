import discord
from discord.ext import commands
from difflib import get_close_matches

@commands.command(name='unmute')
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, *, user_arg=None):
    if not user_arg:
        await ctx.send("Usage: .unmute <user> (mention, ID, or partial name)", delete_after=3)
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
        # Fuzzy match on username and display name
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

    muted_role = discord.utils.get(guild.roles, name="Muted")
    if not muted_role:
        await ctx.send("There is no **Muted** role on this server.", delete_after=3)
        return

    if muted_role not in member.roles:
        await ctx.send(f"**{member.display_name}** is not muted.", delete_after=3)
        return

    if muted_role >= guild.me.top_role:
        await ctx.send("I cannot remove the Muted role because it is higher or equal to my top role.", delete_after=3)
        return

    try:
        await member.remove_roles(muted_role, reason=f"Unmuted by {ctx.author}")
        await ctx.send(f"Unmuted **{member.display_name}** successfully.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to remove the Muted role.", delete_after=3)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to unmute user. Error: **{e}**", delete_after=3)

def setup(bot):
    bot.add_command(unmute)
