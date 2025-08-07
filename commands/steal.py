import discord
from discord.ext import commands
import re
import aiohttp
import random

def make_default_emoji_name(link):
    name = re.findall(r'/([\w\-]+)\.(png|jpg|jpeg|gif)$', link)
    if name and name[0][0]:
        return name[0][0][:30]
    return f"emoji_{random.randint(1000, 9999)}"

@commands.command(name='steal')
@commands.has_permissions(manage_emojis=True)
async def steal(ctx, link: str = None, *, name: str = None):
    guild = ctx.guild

    # If replying to a message with a custom emoji
    if ctx.message.reference and not link:
        try:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        except:
            await ctx.send("**Failed to fetch the replied message.**", delete_after=3)
            return

        match = re.search(r'<(a?):(\w+):(\d+)>', msg.content)
        if not match:
            await ctx.send("**No custom emoji found in the replied message.**", delete_after=3)
            return

        animated, emoji_name, emoji_id = match.groups()
        emoji_url = f'https://cdn.discordapp.com/emojis/{emoji_id}'
        emoji_url += '.gif' if animated == 'a' else '.png'

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(emoji_url) as resp:
                    if resp.status != 200:
                        await ctx.send("**Failed to download the emoji image.**", delete_after=3)
                        return
                    image_bytes = await resp.read()
            except:
                await ctx.send("**Failed to download the emoji image.**", delete_after=3)
                return

        try:
            added_emoji = await guild.create_custom_emoji(name=emoji_name, image=image_bytes)
            await ctx.send(f"Emoji **{added_emoji.name}** added.")
        except discord.Forbidden:
            await ctx.send("**I don't have permission to add emojis.**", delete_after=3)
        except discord.HTTPException as e:
            await ctx.send(f"**Failed to add emoji. Error:** {e}", delete_after=3)
        return

    # If using .steal link [name] style
    if not link:
        await ctx.send("**Usage:** .steal **<image-link>** [**name**] or reply .steal to a message with a custom emoji from any server.", delete_after=3)
        return

    emoji_name = name.replace(' ', '_') if name else make_default_emoji_name(link)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(link) as resp:
                if resp.status != 200:
                    await ctx.send(f"**Failed to download image from link:** {link}", delete_after=3)
                    return
                image_bytes = await resp.read()
        except:
            await ctx.send(f"**Failed to download image from link:** {link}", delete_after=3)
            return

    try:
        added_emoji = await guild.create_custom_emoji(name=emoji_name, image=image_bytes)
        await ctx.send(f"Emoji **{added_emoji.name}** added.")
    except discord.Forbidden:
        await ctx.send("**I don't have permission to add emojis.**", delete_after=3)
    except discord.HTTPException as e:
        await ctx.send(f"**Failed to add emoji. Error:** {e}", delete_after=3)

def setup(bot):
    bot.add_command(steal)
