from discord.ext import commands

@commands.command(name='help')
async def help_command(ctx):
    bot = ctx.bot

    # List all non-hidden commands
    commands_list = [command.name for command in bot.commands if not command.hidden]

    if not commands_list:
        await ctx.send("No commands available.", delete_after=3)
        return

    n = len(commands_list)
    # Split list in half for neatness on long lists
    half = (n + 1) // 2
    line1 = ", ".join(f"**{name}**" for name in commands_list[:half])
    line2 = ", ".join(f"**{name}**" for name in commands_list[half:])

    if line2:
        help_message = f"**Available commands:**\n{line1}\n{line2}"
    else:
        help_message = f"**Available commands:**\n{line1}"

    await ctx.send(help_message)

def setup(bot):
    bot.add_command(help_command)
