import discord
from discord.ext import commands
from difflib import get_close_matches

def find_member(guild, search):
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
    # Fuzzy name match
    if not member:
        names = [m.name for m in guild.members] + [m.display_name for m in guild.members]
        close_names = get_close_matches(search.lower(), [n.lower() for n in names], n=1, cutoff=0.5)
        if close_names:
            for m in guild.members:
                if close_names[0] == m.name.lower() or close_names[0] == m.display_name.lower():
                    member = m
                    break
    return member

def find_voice_channel(guild, search):
    if not search:
        return None
    # Mention
    if search.startswith('<#') and search.endswith('>'):
        try:
            channel_id = int(search.strip('<#>'))
            channel = guild.get_channel(channel_id)
            if isinstance(channel, discord.VoiceChannel):
                return channel
        except:
            return None
    # ID
    if search.isdigit():
        channel = guild.get_channel(int(search))
        if isinstance(channel, discord.VoiceChannel):
            return channel
    # Fuzzy name match
    voice_channels = [c for c in guild.channels if isinstance(c, discord.VoiceChannel)]
    names = [c.name for c in voice_channels]
    close_matches = get_close_matches(search.lower(), [name.lower() for name in names], n=1, cutoff=0.5)
    if close_matches:
        for vc in voice_channels:
            if close_matches[0] == vc.name.lower():
                return vc
    return None

@commands.command(name='move')
async def move(ctx, user_arg=None, *, channel_arg=None):
    if not (ctx.author.guild_permissions.move_members or ctx.author == ctx.guild.owner):
        await ctx.send("**You don't have permission to use this command.**", delete_after=3)
        return
    if not user_arg:
        await ctx.send("**Usage:** .move <user> [voice_channel]", delete_after=3)
        return

    guild = ctx.guild
    member = find_member(guild, user_arg)
    if not member:
        await ctx.send(f"User **{user_arg}** not found.", delete_after=3)
        return

    target_channel = None
    if channel_arg:
        target_channel = find_voice_channel(guild, channel_arg)
        if not target_channel:
            await ctx.send(f"Voice channel **{channel_arg}** not found.", delete_after=3)
            return
    else:
        if ctx.author.voice and isinstance(ctx.author.voice.channel, discord.VoiceChannel):
            target_channel = ctx.author.voice.channel
        else:
            await ctx.send("**You must specify a voice channel if you are not in one.**", delete_after=3)
            return

    if not member.voice or not member.voice.channel:
        await ctx.send(f"User **{member.display_name}** is not in any voice channel.", delete_after=3)
        return

    try:
        await member.move_to(target_channel, reason=f"Moved by {ctx.author}")
        await ctx.send(f"Moved **{member.display_name}** to **{target_channel.name}**.")
    except discord.Forbidden:
        await ctx.send("**I don't have permission to move this user.**", delete_after=3)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to move user. Error: **{e}**", delete_after=3)

@commands.command(name='moveall')
async def moveall(ctx, *, channel_arg=None):
    if not (ctx.author.guild_permissions.move_members or ctx.author == ctx.guild.owner):
        await ctx.send("**You don't have permission to use this command.**", delete_after=3)
        return

    guild = ctx.guild
    target_channel = None
    if channel_arg:
        target_channel = find_voice_channel(guild, channel_arg)
        if not target_channel:
            await ctx.send(f"Voice channel **{channel_arg}** not found.", delete_after=3)
            return
    else:
        if ctx.author.voice and isinstance(ctx.author.voice.channel, discord.VoiceChannel):
            target_channel = ctx.author.voice.channel
        else:
            await ctx.send("**You must specify a voice channel if you are not in one.**", delete_after=3)
            return

    members_to_move = []
    for vc in guild.voice_channels:
        if vc == target_channel:
            continue
        members_to_move.extend(vc.members)

    if not members_to_move:
        await ctx.send("**No users found in other voice channels to move.**", delete_after=3)
        return

    moved_count = 0
    fail_count = 0
    for member in members_to_move:
        try:
            await member.move_to(target_channel, reason=f"Moved by {ctx.author}")
            moved_count += 1
        except:
            fail_count += 1

    message = f"Moved **{moved_count}** members to **{target_channel.name}**."
    if fail_count:
        message += f" Failed to move **{fail_count}** members."
    await ctx.send(message)

def setup(bot):
    bot.add_command(move)
    bot.add_command(moveall)
