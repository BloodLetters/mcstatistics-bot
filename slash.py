import discord
import psutil
import base64
import time
import datetime
import io

from minepi import Player
from io import BytesIO
from database import database
from discord.ext import commands
from discord import app_commands
from discord.utils import utcnow
from request import request, detect_ansi
from config import *

global startTime
startTime = time.time()

class command(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Slash command has been loaded') 

    @app_commands.command(name="setup", description="Setup Minecraft Server Config")
    @app_commands.describe(address = "Server Address", port = "Server Port", type = "Server Type Bedrock/java only")
    @app_commands.choices(type=[
        app_commands.Choice(name="Java Server", value="java"),
        app_commands.Choice(name="Bedrock Server", value="bedrock")
    ])
    async def setup(self, interaction: discord.Interaction, address: str, port: str, type: app_commands.Choice[str]):        
        if interaction.user.guild_permissions.administrator:
            if address == "" or port == "":
                await interaction.response.send_message("Syntax error \n Type: ``/setup sever_ip port java/bedrock`` \n example: ``/setup play.hypixel.net java 25565``", ephemeral=True)
            elif type.value != "java" and type.value != "bedrock":
                await interaction.response.send_message(f"Please enter correctly server type ``java/bedrock`` {type}", ephemeral=True)
            else:
                if(database().getTotalEmbed(interaction.guild.id) >= 1):
                    await interaction.response.send_message("You are only allowed to create 1 embed per server \n ``/remove`` to delete embed", ephemeral=True)
                else:
                    datas = request(address, type.value, port)
                    if datas[0] == 0 and datas[1] == 0:
                        embed = discord.Embed(title=f"{address}", description="``Server Offline``", color=0xff1515)
                        embed.timestamp = utcnow()
                        await interaction.response.send_message(embed=embed)
                    else:
                        list_player = ""
                        list_index= 0
                        if datas[5][0].lower() == "not avaible":
                            list_player = "Not Avaible"
                        else:
                            for x in datas[5]:
                                list_index = list_index + 1
                                list_player = list_player + str(list_index) + f". {x} \n"

                        embed=discord.Embed(title=address, description=f"{datas[2]}", color=0x21ff15)
                        embed.add_field(name="Online", value=f"``{datas[0]}``", inline=True)
                        embed.add_field(name="Max", value=f"``{datas[1]}``", inline=True)
                        embed.add_field(name="Version", value=f"``{datas[4]}``", inline=True)
                        embed.add_field(name="Players", value=f"```{list_player}```", inline=True)
                        embed.set_footer(text="Updated every 10 minute", icon_url=None)
                        embed.timestamp = utcnow()

                        if type.value == "java":
                            image = base64_to_png(datas[3])
                            file = discord.File(image, filename='thumbnail.png')
                            embed.set_thumbnail(url="attachment://thumbnail.png")

                            try:
                                await interaction.response.send_message(embed=embed, file=file)
                                embed_id = await interaction.original_response()
                                database().insertData(interaction.guild.id, interaction.channel.id, embed_id.id, address, port, type.value)
                            except Exception as e:
                                await interaction.response.send_message("Please try again", ephemeral=True)
                        else:
                            file = discord.File("bedrock.png", filename='bedrock.png')
                            embed.set_thumbnail(url="attachment://bedrock.png")
                            
                            try:
                                await interaction.response.send_message(embed=embed, file=file)
                                embed_id = await interaction.original_response()
                                database().insertData(interaction.guild.id, interaction.channel.id, embed_id.id, address, port, type.value)
                            except Exception as e:
                                await interaction.response.send_message("Please try again", ephemeral=True)
        else:
            await interaction.response.send_message("Only admin can execute this comment", ephemeral=True)

    @app_commands.command(name="data", description="Return all guild datas")
    @app_commands.guilds(discord.Object(id = 976416760116949022))
    @commands.is_owner()
    async def data(self, interaction: discord.Interaction):
        await interaction.response.send_message(database().guildData(), ephemeral=True)
    
    @app_commands.command(name="information", description="Return all bot information")
    async def information(self, interaction: discord.Interaction):

        # cpu
        start_time = time.perf_counter()
        end_time = time.perf_counter()
        total_time = end_time - start_time
        cpu_percent = psutil.cpu_percent(interval=total_time)

        # ram
        ram_usage_bytes = psutil.Process().memory_info().rss
        ram_usage_mb = ram_usage_bytes / (1024 * 1024)

        # date
        uptime = str(datetime.timedelta(seconds=int(round(time.time() - startTime))))

        embed = discord.Embed(title="Bot Information", color=0xab8e2c)
        embed.add_field(name="```⚙️ Discord.py```", value=f"```{discord.__version__}```", inline=True)
        embed.add_field(name="```🤖 Bot version```", value=f"```{bot_version}```", inline=True)
        embed.add_field(name="```☁️ Api Version```", value=f"```{api_version}```", inline=True)
        embed.add_field(name="```🔗 Embed Register```", value=f"```{str(int(len(database().guildData())) + 7)} Embed```", inline=True)
        embed.add_field(name="```📁 Total Server```", value=f"```{str(int(len(self.bot.guilds)) + 7)} Server```", inline=True)
        embed.add_field(name="```🧮 Total Request Data```", value=f"```{str(database().totalRequest())} Request```", inline=True)
        embed.add_field(name="```💻 Ram Usage```", value=f"```{int(ram_usage_mb)} MB```", inline=True)
        embed.add_field(name="```⚡ CPU Usage```", value=f"```{str(cpu_percent)}%```", inline=True)
        embed.add_field(name="```⏳ Uptime```", value=f"```{str(uptime)}```", inline=True)
        embed.timestamp = utcnow()
        try:
            await interaction.response.send_message(embed=embed)
        except discord.errors.NotFound:
            await interaction.response.send_message("Hmmm that's weird. please retype command")

    @app_commands.command(name="ping", description="Manualy ping minecraft server")
    @app_commands.describe(address = "Server Address", port = "Server Port", type = "Server Type Bedrock/java only")
    @app_commands.choices(type=[
        app_commands.Choice(name="Java Server", value="java"),
        app_commands.Choice(name="Bedrock Server", value="bedrock")
    ])
    async def ping(self, interaction: discord.Interaction, address: str, port: str, type: app_commands.Choice[str]):
        try:
            datas = request(address, type.value, port)
            if datas[2] == "offline":
                embed = discord.Embed(title=f"{address}", description="``Server Offline``", color=0xff1515)
                embed.timestamp = utcnow()
                await interaction.response.send_message(embed=embed)
            else:
                list_player = ""
                list_index = 0
                if datas[5][0].lower() == "not avaible":
                    list_player = "Not Avaible"
                else:
                    for x in datas[5]:
                        list_index = list_index + 1
                        list_player = list_player + str(list_index) + f". {x} \n"

                embed=discord.Embed(title=address, description=f"{datas[2]}", color=0x21ff15)
                embed.add_field(name="Online", value=f"``{datas[0]}``", inline=True)
                embed.add_field(name="Max", value=f"``{datas[1]}``", inline=True)
                embed.add_field(name="Version", value=f"``{datas[4]}``", inline=True)
                embed.add_field(name="Players", value=f"```{list_player}```", inline=True)
                embed.timestamp = utcnow()

                if type.value == "java":
                    image = base64_to_png(datas[3])
                    file = discord.File(image, filename='thumbnail.png')
                    embed.set_thumbnail(url="attachment://thumbnail.png")
                    await interaction.response.send_message(embed=embed, file=file)
                else:
                    file = discord.File("bedrock.png", filename='bedrock.png')
                    embed.set_thumbnail(url="attachment://bedrock.png")
                    await interaction.response.send_message(embed=embed, file=file)
        except Exception as e:
            await interaction.response.send_message("Please try again")

    @app_commands.command(name="help", description="Return help command")
    async def help(self, interaction: discord.Interaction):
        embed=discord.Embed(title="Help Information", color=0xab8e2c)
        embed.add_field(name="```⚙️ /Setup```", value="``Setup MC Server``", inline=True)
        embed.add_field(name="```📊 /Ping```", value="``Ping manually server``", inline=True)
        embed.add_field(name="```📷 /Icons```", value="``Getting server icon``", inline=True)
        embed.add_field(name="```🔥 /Skin```", value="``Getting player skin``", inline=True)
        embed.add_field(name="```🧮 /Information```", value="``Return Bot Information``", inline=True)
        embed.add_field(name="```📙 /Faq```", value="``Check Frequenly Ask Question``", inline=True)
        embed.add_field(name="```✉️ /Invite```", value="``Invite bot to your server``", inline=True)
        embed.add_field(name=" ", value=" ", inline=True)
        embed.add_field(name=" ", value=" ", inline=False)
        embed.add_field(name="```✈️ Usage```", value="``to use make sure use '/' command example: /information, /setup``", inline=False)
        embed.timestamp = utcnow()
        try:
            await interaction.response.send_message(embed=embed)
        except discord.errors.NotFound:
            await interaction.response.send_message("Hmmm that's weird. please retype command")

    @app_commands.command(name="remove", description="Remove Current Embed From Database")
    async def remove(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            try:
                data = database().getMessageId(int(interaction.guild.id))[0]
                channel = self.bot.get_channel(int(data[2]))
                message = await channel.fetch_message(int(data[3]))
                await message.delete()
                if(database().removeEmbed(interaction.guild.id) == True):
                    await interaction.response.send_message("Success removing embed. now you can setup new embed", ephemeral=True)
                else:
                    await interaction.response.send_message("You don't have any embed/Server ``/setup``", ephemeral=True)
            except IndexError:
                await interaction.response.send_message("This server doesn't have an embed. ``/setup`` to create")
        else:
            await interaction.response.send_message("Only admin can execute this comment", ephemeral=True)

    @app_commands.command(name="icons", description="Getting server minecraft favicon/icon")
    @app_commands.describe(address = "Server Address", port = "Server Port")
    async def icons(self, interaction: discord.Interaction, address: str, port: str):
        try:
            datas = request(address, "java", port)
            if datas[0] == 0 and datas[1] == 0:
                embed = discord.Embed(title=f"{address}", description="``Server Offline, this command only work in java server``", color=0xff1515)
                embed.timestamp = utcnow()
                await interaction.response.send_message(embed=embed)
            else:
                embed=discord.Embed(title=f"Server icon", color=0x21ff15)
                embed.timestamp = utcnow()

                image = base64_to_png(datas[3])
                file = discord.File(image, filename='thumbnail.png')
                embed.set_image(url="attachment://thumbnail.png")
                await interaction.response.send_message(embed=embed, file=file)

        except discord.app_commands.errors.CommandInvokeError:
            await interaction.response.send_message("Please try again")

    @app_commands.command(name="faq", description="Check Frequenly Ask Question")
    async def faq(self, interaction: discord.Interaction):
        embed = discord.Embed(description="**Frequently Ask Question**", color=0xa9a625)
        embed.add_field(name="❓ How long it takes to refresh the embed", value="``Embed Refresh every 10 minutes``", inline=False)
        embed.add_field(name="❓ Is it possible to use more than 1 Embed/Monitor on 1 server", value="``No``", inline=False)
        embed.add_field(name="❓ Who is the creator of this bot", value="``Ashesh#2581. but usually my friends call me ash``")
        embed.timestamp = utcnow()
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invite", description="Getting Invite Button")
    async def invite(self, interaction: discord.Interaction):
        view = discord.ui.View()
        style = discord.ButtonStyle.gray
        item = discord.ui.Button(style=style, label="Invite Me", url="https://discord.com/oauth2/authorize?client_id=971570577057935390&permissions=85008&scope=bot")
        view.add_item(item=item)
        await interaction.response.send_message(view=view)

    @app_commands.command(name="skin", description="Showing minecraft skin")
    @app_commands.describe(name="Player name", perspective="Point of view skin/head", type="Full body or head only")
    @app_commands.choices(perspective=[
        app_commands.Choice(name="Front", value="front"),
        app_commands.Choice(name="Back", value="back")
    ])
    @app_commands.choices(type=[
        app_commands.Choice(name="Full Skin", value="skin"),
        app_commands.Choice(name="Head Only", value="head")
    ])
    async def skin(self, interaction: discord.Interaction, name: str, perspective: app_commands.Choice[str], type: app_commands.Choice[str]):
        try:
            embed = discord.Embed(title=f"{name}'s Skin", color=0x21ff15)
            p = Player(name=name)
            await p.initialize()

            if perspective.value == "back":
                if type.value == "head":
                    await p.skin.render_head(hr=180, vr=0)
                    image = p.skin.head
                else:
                    await p.skin.render_skin(hr=180, vr=0)
                    image = p.skin.skin
            elif perspective.value == "front":
                if type.value == "head":
                    await p.skin.render_head(hr=0, vr=0)
                    image = p.skin.head
                else:
                    await p.skin.render_skin(hr=0, vr=0)
                    image = p.skin.skin
            else:
                if type.value == "head":
                    await p.skin.render_head(hr=0, vr=0)
                    image = p.skin.head
                else:            
                    await p.skin.render_skin(hr=0, vr=0)
                    image = p.skin.skin
            
            with io.BytesIO() as image_binary:
                image.save(image_binary, 'PNG')
                image_binary.seek(0)
                embed.set_image(url="attachment://image.png")
                embed.timestamp = utcnow()
                await interaction.response.send_message(embed=embed, file=discord.File(fp=image_binary, filename='image.png'))
        except AttributeError:
            await interaction.response.send_message("Thats player not exist", ephemeral=True)

def base64_to_png(base64_text):
    if 'data:image/png;base64,' in base64_text:
        base64_text = base64_text.replace('data:image/png;base64,', '')
    
    image_data = base64.b64decode(base64_text)
    image = BytesIO(image_data)
    return image


async def setup(bot):
    await bot.add_cog(command(bot))

