import discord

from database import database
from discord.ext import commands

class slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup(self, ctx, server_ip="", port="", server_type=""):
        if server_ip == "" or port == "":
            await ctx.send("Syntax error \n Type: ``!setup sever_ip port java/bedrock`` \n example: ``!setup play.hypixel.net java 25565``")
        elif server_type != "java" and server_type != "bedrock":
            await ctx.send("Please enter correctly server type ``java/bedrock``")
        else:
            embed = discord.Embed(title="Setup Success", description=f"Please wait to bot reload this embed \n \n IP: {server_ip} \n Port: {port} \n Type: {server_type}", color=0x21ff15)
            embed_id = await ctx.send(embed=embed)
            database().insertData(ctx.guild.id, ctx.channel.id, embed_id.id, server_ip, port, server_type)

    @commands.command()
    async def data(self, ctx):
        await ctx.send(database().guildData())
    
async def setup(bot):
    await bot.add_cog(slash(bot))