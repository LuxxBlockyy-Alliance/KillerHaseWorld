from discord.ext import commands
import aiohttp
from discord import Webhook
import run
from source import tools
import discord
import datetime


class GlobalChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook_session = aiohttp.ClientSession()

    async def send_global_message(self, server_name: str, author_icon: str, message: str, author: str, avatar_url: str,
                                  footer: dict, fields: list, thumbnail_url: str = None):
        for url in await tools.get_column("./source/world.db", "world_chats", "webhook_url"):
            try:
                webhook = Webhook.from_url(str(url), session=self.webhook_session)
                e = await tools.create_embed(server_name, author_icon, author, message, avatar_url, footer, fields,
                                             thumbnail_url)
                a = e.copy()
                await webhook.send(embed=e, avatar_url="https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png")
            except discord.NotFound as e:
                print("Well some error, may there be a webhook in db that doesn't exist")
                pass

    async def get_webhook(self, channel_id):
        try:
            print(1)
            channel = self.bot.get_channel(channel_id)
            print(2)
            if not channel:
                print("NO channel")
                return None
            print(3)
            webhooks = await channel.webhooks()
            print(4)
            webhook = discord.utils.get(webhooks, name="GlobalChat")
            print(5)
            if not webhook:
                print("Webhook existiert nicht")
                webhook = await channel.create_webhook(name="GlobalChat")
                print(webhook.url)
                return webhook.url
                # async with aiohttp.ClientSession() as session:
                #    async with session.get("https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png") as resp:
                #        if resp.status == 200:
                #            data = await resp.read()
                #            webhook = await channel.create_webhook(name="GlobalChat")
                #        else:
                #            return None
            return webhook.url
        except Exception as e:
            print(e.with_traceback(e))

    async def deletewebhook(self, channel_id):
        try:
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                return None
            webhooks = await channel.webhooks()
            globalhook = None
            for webhook in webhooks:
                if webhook.name == "GlobalChat":
                    globalhook = webhook
                    break
            if globalhook:
                await globalhook.delete()
        except Exception as e:
            print(e.with_traceback(e))

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send("No Permission, yk yk.")

    @discord.slash_command(description="Füge einen Channel in unsere Datenbank ein")
    async def addglobal(self, ctx, channel: discord.TextChannel):
        print(channel.name)
        # async with self.bot.pool.acquire() as conn:
        if await tools.view_dat_row(await tools.get_DB_path(), "world_chats", "channel_id", channel.id):
            print("1")
            await ctx.respond(
                f"{channel.mention} ist bereits ein global chat zum entfernen benutze /removeglobal <channel>")
        else:
            print("-")
            webhook = await self.get_webhook(channel.id)
            print(webhook)
            try:
                server_invite = self.bot.create_ivite(channel.guild)
                print("--")
                db = await tools.get_DB_path()
                print("---")
                id = await tools.get_next_id(db, "world_chats")
                print(f"db, 'world_chats', {id}, {channel.id}, {webhook}, {ctx.guild.id}, {server_invite}")
                await tools.insert_data(db, "world_chats", id, channel.id, webhook, ctx.guild.id, server_invite)
                print("------")
                await ctx.respond(f"{channel.mention} wurde zum Global Chat hinzugefügt.")
                print("000000000")
            except Exception as e:
                print("WELL there was a error")
                print(e.with_traceback(e))

    @discord.slash_command(description="Entferne den Globalchat aus unserer Datenbank.")
    async def removeglobal(self, ctx, channel: discord.TextChannel):
        # async with self.bot.pool.acquire() as conn:
        db = await tools.get_DB_path()
        await tools.delete_data(db, "world_chats", f"{channel.id}")
        await self.deletewebhook(channel.id)
        await ctx.respond(f"{channel.mention} wurde vom Global Chat entfernt.")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        db = await tools.get_DB_path()
        await tools.delete_server_data(db, "world_chats", f"{guild.id}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        db = await tools.get_DB_path()
        await tools.delete_data(db, "world_chats", f"{channel.id}")

    @discord.slash_command(description="Eine menge Hilfe zum Globalchat :)")
    async def help(self, ctx):
        embed = discord.Embed(
            title="Hilfeee",
            description="Eine menge Hilfe zum Globalchat :)",
            color=discord.Colour.red(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Um einen globalchat hinzuzufügen benutze:", value="```bash\n/addglobal <channel_id>\n```",
                        inline=False)
        embed.add_field(name="Um einen globalchat zu entfernen benutze:",
                        value="```bash\n/removeglobal <channel_id>\n```", inline=False)
        embed.add_field(name="Um dir das hier anzeigen zu lassen benutze:", value="```bash\n/help\n```", inline=False)
        embed.add_field(name="Für weitere hilfe tritt unserem Discord bei:", value="https://join.killerhase75.com",
                        inline=False)
        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            try:
                for channel_id in await tools.get_column(await tools.get_DB_path(), "world_chats", "channel_id"):
                    if int(channel_id[0]) == message.channel.id:
                        if message.content.contains("https:") or message.content.contains("http:") or message.content.contains("www."):
                            print("May be an AD!!!")
                        db = await tools.get_DB_path()
                        server_text = f"[{message.guild.name}"
                        footer = {
                            "icon_url": self.bot.user.avatar,
                            "text": f"Server anzahl: {await run.get_server_count()}"
                        }
                        fields = [
                            {'name': '', 'value': '🤖 [Invite mich](https://world.killerhase75.com)', 'inline': True}
                        ]
                        if message.author.avatar and message.guild.icon:
                            await self.send_global_message(f"", message.guild.icon, message.content,
                                                           message.author.display_name, message.author.avatar.url,
                                                           footer,
                                                           fields, message.author.avatar)
                        elif message.author.avatar:
                            await self.send_global_message(message.guild.name,
                                                           "https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png",
                                                           message.content,
                                                           message.author.display_name, message.author.avatar.url,
                                                           footer,
                                                           fields, message.author.avatar)
                        elif message.guild.icon:
                            await self.send_global_message(message.guild.name, message.guild.icon, message.content,
                                                           message.author.display_name,
                                                           "https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png",
                                                           footer,
                                                           fields, message.author.avatar)
                        else:
                            await self.send_global_message(message.guild.name,
                                                           "https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png",
                                                           message.content,
                                                           message.author.display_name,
                                                           "https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png", footer,
                                                           fields)
                        # await self.send_global_message(message.content, message.author.display_name,
                        # message.author.avatar
                        await message.delete()
            except TypeError as e:
                print("Database get column returned NONE")

        pass


def setup(bot):
    bot.add_cog(GlobalChat(bot))
