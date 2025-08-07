import discord
from discord.ext import commands
from difflib import get_close_matches

@commands.command(name='role')
@commands.has_permissions(manage_roles=True)
async def role(ctx, user_arg=None, *, role_arg=None):
    # If only one argument provided, treat as role for command author
    if role_arg is None:
        role_arg = user_arg
        member = ctx.author
    else:
        member = None
        search = user_arg

        # Try mention
        if search and search.startswith('<@') and search.endswith('>'):
            try:
                user_id = int(search.strip('<@!>'))
                member = ctx.guild.get_member(user_id)
            except:
                pass

        # Try ID
        if not member and search and search.isdigit():
            member = ctx.guild.get_member(int(search))

        # Fuzzy match
        if not member and search:
            names = [m.name for m in ctx.guild.members] + [m.display_name for m in ctx.guild.members]
            close_names = get_close_matches(search.lower(), [n.lower() for n in names], n=1, cutoff=0.5)
            if close_names:
                for m in ctx.guild.members:
                    if close_names[0] == m.name.lower() or close_names[0] == m.display_name.lower():
                        member = m
                        break

        if not member:
            await ctx.send(f"Could not find a user matching **{search}**.", delete_after=3)
            return

    # Helper to find role by mention, id, or fuzzy name
    def find_role(search):
        role = None
        if search and search.startswith('<@&') and search.endswith('>'):
            try:
                role_id = int(search.strip('<@&>'))
                role = ctx.guild.get_role(role_id)
            except:
                pass
        if not role and search and search.isdigit():
            role = ctx.guild.get_role(int(search))
        if not role and search:
            role_names = [r.name for r in ctx.guild.roles]
            close_role = get_close_matches(search.lower(), [r.lower() for r in role_names], n=1, cutoff=0.5)
            if close_role:
                for r in ctx.guild.roles:
                    if close_role[0] == r.name.lower():
                        role = r
                        break
        return role

    role = find_role(role_arg)
    if not role:
        await ctx.send(f"Could not find a role matching **{role_arg}**.", delete_after=3)
        return

    if role >= ctx.guild.me.top_role:
        await ctx.send("I cannot assign or remove a role equal or higher than my highest role.", delete_after=3)
        return

    try:
        if role in member.roles:
            await member.remove_roles(role, reason=f"Toggled by {ctx.author}")
            await ctx.send(f"Removed the role **{role.name}** from **{member.display_name}**.")
        else:
            await member.add_roles(role, reason=f"Toggled by {ctx.author}")
            await ctx.send(f"Gave the role **{role.name}** to **{member.display_name}**.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to modify that role.", delete_after=3)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to toggle role. Error: **{e}**", delete_after=3)

def setup(bot):
    bot.add_command(role)
