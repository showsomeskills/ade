import discord
from discord.ext import commands
from difflib import get_close_matches

@commands.command(name='av')
async def av(ctx, *, user_arg=None):
    guild = ctx.guild

    def find_member(search):
        member = None
        if not search:
            return None
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
        # Fuzzy match
        if not member:
            names = [m.name for m in guild.members] + [m.display_name for m in guild.members]
            close = get_close_matches(search.lower(), [n.lower() for n in names], n=1, cutoff=0.5)
            if close:
                for m in guild.members:
                    if close[0] == m.name.lower() or close[0] == m.display_name.lower():
                        member = m
                        break
        return member

    if user_arg:
        member = find_member(user_arg)
        if not member:
            await ctx.send(f"Could not find a user matching **{user_arg}**.", delete_after=3)
            return
    else:
        member = ctx.author

    avatar_url = member.display_avatar.url
    embed = discord.Embed(title=f"Avatar of **{member.display_name}**")
    embed.set_image(url=avatar_url)
    # Add "Requested by" in the footer
    embed.set_footer(text=f"Requested by {ctx.author.display_name}")

    await ctx.send(embed=embed)

def setup(bot):
    bot.add_command(av)
