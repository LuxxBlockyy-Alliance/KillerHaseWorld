from discord.ext import commands
import aiohttp
from discord import Webhook, NotFound
import run
from source import tools
import discord
import datetime


class GlobalChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook_session = aiohttp.ClientSession()

    async def send_global_message(self, server_name: str, author_icon: str, author_url: str, message: str, author: str,
                                  avatar_url: str,
                                  footer: dict, fields: list, thumbnail_url: str = None):
        for url in await tools.get_column("./source/world.db", "world_chats", "webhook_url"):
            try:
                webhook = Webhook.from_url(str(url), session=self.webhook_session)
                e = await tools.create_embed(server_name, author_icon, author_url, author, message, avatar_url, footer,
                                             fields,
                                             thumbnail_url)
                a = e.copy()
                await webhook.send(embed=e, avatar_url="https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png")
            except discord.NotFound as e:
                print("Well some error, may there be a webhook in db that doesn't exist")
                pass

    async def get_webhook(self, channel_id):
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                return None
            webhooks = await channel.webhooks()
            webhook = discord.utils.get(webhooks, name="GlobalChat")
            if not webhook:
                webhook = await channel.create_webhook(name="GlobalChat")
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
        # async with self.bot.pool.acquire() as conn:
        if await tools.view_dat_row(await tools.get_DB_path(), "world_chats", "channel_id", channel.id):
            embed = discord.Embed(
                title="⚠️ Fehler ⚠️",
                description="Der Channel ist bereits eingetragen!",
                color=discord.Colour.red(),
                timestamp=datetime.datetime.now()
            )
            await ctx.respond(embed=embed)
        else:
            webhook = await self.get_webhook(channel.id)
            try:
                try:
                    server_invite = await channel.create_invite(
                        reason="Globalchat Invite Link",
                        max_age=0,
                        max_uses=0
                    )
                except Exception as e:
                    print(f"ERR: {e}")
                    pass
                db = await tools.get_DB_path()
                ident = await tools.get_next_id(db, "world_chats")
                await tools.insert_data(db, "world_chats", ident, channel.id, webhook, ctx.guild.id, server_invite)
                embed = discord.Embed(
                    title="Willkommen!",
                    description="Der Channel wurde erfolgreich hinzugefügt...",
                    color=discord.Colour.green(),
                    timestamp=datetime.datetime.now()
                )
                await ctx.respond(embed=embed)
                footer = {
                    "icon_url": self.bot.user.avatar,
                    "text": f"Server anzahl: {await run.get_server_count()}"
                }
                footer_icon = footer.get("icon_url")
                footer_text = footer.get("text")
                fields = [
                    {'name': '', 'value': '🤖 [Invite mich](https://world.killerhase75.com)', 'inline': True}
                ]
                try:
                    embed = discord.Embed(
                        title="Herzlich Willkommen ❤️",
                        description=f"{channel.guild.name} ist uns beigetreten",
                        color=discord.Colour.green(),
                        timestamp=datetime.datetime.now()
                    )
                    if not channel.guild.icon:
                        guild_icon = "https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png"
                    else:
                        guild_icon = channel.guild.icon.url
                    embed.set_thumbnail(url=guild_icon)
                    embed.set_author(name=channel.guild.name, icon_url=guild_icon,
                                     url="https://world.killerhase75.com")
                    embed.set_footer(text=footer_text, icon_url=footer_icon)
                    for url in await tools.get_column("./source/world.db", "world_chats", "webhook_url"):
                        try:
                            webhook = Webhook.from_url(str(url), session=self.webhook_session)
                            await webhook.send(embed=embed, avatar_url="https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png")
                        except discord.NotFound as e:
                            print("Well some error, may there be a webhook in db that doesn't exist")
                            pass
                except Exception as e:
                    print(e)
            except Exception as e:
                try:
                    await ctx.respond(f"Janosch hat das await vergessen, oder was anderes Kaputt gemacht!")
                except:
                    pass
                print(f"WELL there was a error: {e}")
                print(e.with_traceback(e))

    @discord.slash_command(description="Entferne den Globalchat aus unserer Datenbank.")
    async def removeglobal(self, ctx, channel: discord.TextChannel):
        # async with self.bot.pool.acquire() as conn:
        db = await tools.get_DB_path()
        if await tools.view_dat_row(await tools.get_DB_path(), "world_chats", "channel_id", channel.id):
            server_invite = await tools.view_data_one(db, "world_chats", "guild_id", channel.guild.id, "guild_invite")
            await tools.delete_data(db, "world_chats", f"{channel.id}")
            await self.deletewebhook(channel.id)
            embed = discord.Embed(
                title="Ciao!",
                description="Der Channel wurde erfolgreich entfernt...",
                color=discord.Colour.red(),
                timestamp=datetime.datetime.now()
            )
            await ctx.respond(embed=embed)
            ###
            footer = {
                "icon_url": self.bot.user.avatar,
                "text": f"Server anzahl: {await run.get_server_count()}"
            }
            footer_icon = footer.get("icon_url")
            footer_text = footer.get("text")
            fields = [
                {'name': '', 'value': '🤖 [Invite mich](https://world.killerhase75.com)', 'inline': True}
            ]
            try:
                embed = discord.Embed(
                    title="Ciao... 😔",
                    description=f"{channel.guild.name} hat uns leider Verlassen...",
                    color=discord.Colour.red(),
                    timestamp=datetime.datetime.now()
                )
                if not channel.guild.icon:
                    icon_url = "https://i.ibb.co/D96qZq7/KH75-World-Chat.png"
                else:
                    icon_url = channel.guild.icon.url

                print(icon_url)

                embed.set_thumbnail(url=icon_url)
                embed.set_author(name=channel.guild.name, icon_url=icon_url, url="https://world.killerhase75.com")
                embed.set_footer(text=footer_text, icon_url=footer_icon)
                for url in await tools.get_column("./source/world.db", "world_chats", "webhook_url"):
                    try:
                        webhook = Webhook.from_url(str(url), session=self.webhook_session)
                        await webhook.send(embed=embed, avatar_url="https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png")
                    except discord.NotFound as e:
                        print("Well some error, may there be a webhook in db that doesn't exist")
                        pass
            except Exception as e:
                print(e)

        else:
            embed = discord.Embed(
                title="⚠️ Fehler ⚠️",
                description="Der Channel ist nicht eingetragen!",
                color=discord.Colour.red(),
                timestamp=datetime.datetime.now()
            )
            await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        db = await tools.get_DB_path()
        await tools.delete_server_data(db, "world_chats", f"{guild.id}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        db = await tools.get_DB_path()
        await tools.delete_data(db, "world_chats", f"{channel.id}")

    @commands.Cog.listener()
    async def on_raw_webhook_update(self, payload):
        # Ignore the event if the webhook was not deleted
        if payload.data["type"] != 1:
            return

        # Retrieve the guild object from the cache
        guild = self.bot.get_guild(payload.guild_id)

        # Check if the webhook was deleted
        try:
            webhook = await guild.fetch_webhook(payload.webhook_id)
        except NotFound:
            # If a NotFound error is raised, it means the webhook was deleted
            print(f"Webhook with ID {payload.webhook_id} was deleted")

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
                        db = await tools.get_DB_path()
                        server_text = f"[{message.guild.name}"
                        footer = {
                            "icon_url": self.bot.user.avatar,
                            "text": f"Server anzahl: {await run.get_server_count()}"
                        }
                        fields = [
                            {'name': '', 'value': '🤖 [Invite mich](https://world.killerhase75.com)', 'inline': True}
                        ]
                        server_invite = await tools.view_data_one(db, "world_chats", "guild_id", message.guild.id,
                                                                  "guild_invite")
                        if server_invite:
                            server_invite = server_invite[0]
                        if message.author.avatar and message.guild.icon:
                            await self.send_global_message(message.guild.name, message.guild.icon,
                                                           f"{server_invite[0]}", message.content,
                                                           message.author.display_name, message.author.avatar.url,
                                                           footer,
                                                           fields, message.author.avatar)
                        elif message.author.avatar:
                            await self.send_global_message(message.guild.name,
                                                           "https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png",
                                                           f"{server_invite[0]}",
                                                           message.content,
                                                           message.author.display_name, message.author.avatar.url,
                                                           footer,
                                                           fields, message.author.avatar)
                        elif message.guild.icon:
                            await self.send_global_message(message.guild.name, message.guild.icon,
                                                           f"{server_invite[0]}", message.content,
                                                           message.author.display_name,
                                                           "https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png",
                                                           footer,
                                                           fields, message.author.avatar)
                        else:
                            await self.send_global_message(message.guild.name,
                                                           "https://i.ibb.co/D96qZq7/KH75-World-Chat-2.png",
                                                           f"{server_invite[0]}",
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
