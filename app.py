import discord
import asyncio
import base64
import datetime
import zipfile
import pytz
import os

from PIL import Image
from io import BytesIO
from config import *
from database import database, counter
from discord.ext import commands
from discord.utils import utcnow
from request import request
from discord.ext.commands import CommandNotFound

# Inisialisasi bot
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')
start_time = datetime.datetime.now()

# Event handler on_ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/help"))

    # cogs
    for cog in initial_cogs:
        try:
            await bot.load_extension(cog)
            print(f'Loaded cog: {cog}')
        except Exception as e:
            print(f'Failed to load cog: {cog}\n{type(e).__name__}: {e}')

    # slash command
    try:
        sync = await bot.tree.sync()
        print(f"Registering {len(sync)} slash commands")
    except Exception as e:
        print(e)
    
    if update_embed == True:
        bot.loop.create_task(server_reload())
    
    if use_backup == True:
        bot.loop.create_task(backup())
    #await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/help"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    
@bot.command()
@commands.is_owner()
async def reload(ctx):
    if ctx.channel.id == 1094282467977998359:
        reloaded = []
        error = []
        for cog in initial_cogs:
            try:
                await bot.reload_extension(cog)
                reloaded.append(cog)
            except Exception as e:
                error.append(cog)
        await ctx.send(f'Cog Reload: {reloaded} \n Cog Error: {error}')


@bot.tree.command(name="reload", description="Reload All command", guild = discord.Object(id = 976416760116949022))
@commands.is_owner()
async def reload(interaction: discord.Interaction):
    reloaded = []
    error = []
    for cog in initial_cogs:
        try:
            await bot.reload_extension(cog)
            reloaded.append(cog)
        except Exception as e:
            error.append(cog)
    await interaction.response.send_message(f'Cog Reload: {reloaded} \n Cog Error: {error}')

def update_data():
    guild = len(bot.guilds)
    t_channel = 0
    t_member = 0

    for member in bot.guilds:
        t_member = member.member_count + t_member

    for channel in bot.guilds:
        t_channel = len(channel.text_channels) + t_channel

    counter().setData(guild, t_member, t_channel)

async def server_reload():
    while True:
        update_data()
        for x in database().guildData():
            database().insertRequest(int(x[1]))
            channel = bot.get_channel(x[2])
            try:
                message = await channel.fetch_message(x[3])
                datas = request(x[4], x[5], x[6])
                if datas[0] == 0 and datas[1] == 0:
                    embed = discord.Embed(title=f"{x[4]}", description="``Server Offline``", color=0xff1515)
                    embed.timestamp = utcnow()
                    await message.edit(embed=embed)
                    await asyncio.sleep(5)
                else:
                    list_player = ""
                    list_index = 0
                    if datas[5][0].lower() == "not avaible":
                        list_player = "Not Avaible"
                    else:
                        for pla in datas[5]:
                            list_index = list_index + 1
                            list_player = list_player + str(list_index) + f". {pla} \n"

                    embed = discord.Embed(title=x[4], description=f"{datas[2]}", color=0x21ff15)
                    embed.add_field(name="Online", value=f"``{datas[0]}``", inline=True)
                    embed.add_field(name="Max", value=f"``{datas[1]}``", inline=True)
                    embed.add_field(name="Version", value=f"``{datas[4]}``", inline=True)
                    embed.add_field(name="Players", value=f"```{list_player}```", inline=True)
                    embed.set_footer(text="Updated every 10 minute", icon_url=None)
                    embed.timestamp = utcnow()

                    if x[5] == "java":
                        image = base64_to_png(datas[3])
                        gambar = Image.open(image)

                        buffer = BytesIO()
                        
                        # except type 
                        try:
                            gambar.save(buffer, format='JPEG')
                        except Exception as e:
                            print(f"{getTime()} -> Exception ditemukan: {e}")
                            if e == "cannot write mode RGBA as JPEG":
                                gambar.save(buffer, format='RGBA')
                                print(f"{getTime()} -> Execption RGBA berhasil di atasi")

                        buffer.seek(0)
                        embed.set_thumbnail(url="attachment://thumbnail.png")

                        await message.edit(embed=embed)
                        await asyncio.sleep(5)
                    else:
                    
                        embed.set_thumbnail(url="attachment://bedrock.png")
                        await message.edit(embed=embed)
                        await asyncio.sleep(5)

            except (AttributeError, discord.errors.NotFound):
                database().deleteData(int(x[0]))

        await asyncio.sleep(embed_reload_time)

async def getTime():
    timezone = pytz.timezone("Asia/Makassar")
    waktu_sekarang = datetime.datetime.now(timezone).strftime("%Y-%m-%d")
    return waktu_sekarang

async def compress_folder(folder_path, exclude_folders, zip_filename):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            if not any(exclude_folder in root for exclude_folder in exclude_folders):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, folder_path))

async def backup():
    while True:
        try:
            folder_path = '/'
            exclude_folders = ['./__pycache__', './.vscode', './.cache', './.local']
            time = await getTime()
            zip_filename = f'./backup/{time}.zip'
            await compress_folder(folder_path, exclude_folders, zip_filename)
            #print(f'Selesai mengompresi folder {folder_path} ke dalam file {zip_filename}.')
            channel = bot.get_channel(1095669231166705704)
            await channel.send(file=discord.File(zip_filename))
            print("Backup berhasil!")
        except AttributeError:
            pass
        await asyncio.sleep(backup_time)

def base64_to_png(base64_text):
    if 'data:image/png;base64,' in base64_text:
        base64_text = base64_text.replace('data:image/png;base64,', '')
    
    image_data = base64.b64decode(base64_text)
    image = BytesIO(image_data)
    return image

if __name__ == "__main__":
    # Jalankan bot
    bot.run('OTcxNTcwNTc3MDU3OTM1Mzkw.G_uy64.D_HyUN51J0My2rDbBd3CU7UpU2kb-o01xQ4XhU')  # Ganti dengan token bot Anda