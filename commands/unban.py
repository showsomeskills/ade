import discord
from discord.ext import commands

@commands.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, user_arg=None):
    if user_arg is None:
        await ctx.send(
            "Please specify a user to unban by full tag (e.g. Username#1234) or user ID.\n"
            "Example usage:\n"
            ".unban Username#1234\n"
            ".unban 123456789012345678",
            delete_after=5
        )
        return

    # Retrieve all bans
    bans = []
    async for entry in ctx.guild.bans():
        bans.append(entry)

    user = None

    # Try finding user by ID
    if user_arg.isdigit():
        user_id = int(user_arg)
        for entry in bans:
            if entry.user.id == user_id:
                user = entry.user
                break

    # Try finding user by full username#discriminator
    if not user and "#" in user_arg:
        try:
            name, discriminator = user_arg.split("#", 1)
        except ValueError:
            await ctx.send("Please provide the full Discord tag in the format Username#1234.", delete_after=5)
            return
        for entry in bans:
            if (entry.user.name, entry.user.discriminator) == (name, discriminator):
                user = entry.user
                break

    if not user:
        await ctx.send(f"Could not find a banned user matching **{user_arg}**. Use full tag or user ID.", delete_after=5)
        return

    try:
        await ctx.guild.unban(user)
        await ctx.send(f"Successfully unbanned **{user.name}#{user.discriminator}**.")
    except discord.Forbidden:
        await ctx.send("I do not have permission to unban this user.", delete_after=3)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to unban user. Error: **{e}**", delete_after=3)

def setup(bot):
    bot.add_command(unban)
