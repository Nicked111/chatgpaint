import discord
from discord.ext import commands
import os
import json

from dotenv import load_dotenv
load_dotenv()
environment = os.getenv("ENVIRONMENT")
data_path = None
if environment == "DEV": data_path = "./../data"
elif environment == "PROD": data_path = "/db"

class AdminCommands(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.command(name="role-colors") # this is a command that can be used by users
    @commands.is_owner()
    async def roleColors(self, ctx): # the first argument of a command is always the context
        rolecolors = {
                1341767688384675861: "🍏",
                1341767941586423930: "🍎",
                1341767941586423930: "🍐",
                1341768071030898688: "🍊",
                1341768035932835861: "🍋",
                1341766810286161940: "🍋‍🟩",
                1341768096419025068: "🍌",
                1341767290328453212: "🍉",
                1341766887981318164: "🍇",
                1341767441658941470: "🍓",
                1341766994432622653: "🫐",
                1341768250564022384: "🍈",
                1341768940640272488: "🍒",
                0: "❌"
        }
        embedText = ""
        for role in rolecolors:
            if role == 0: continue
            embedText += f"{rolecolors[role]} - <@&{role}>\n"
        embed = discord.Embed(title="Role colors", description=embedText)
        embed.color = 0x1abc9c
        embed.set_footer(text=f"To remove your color, react with ❌")
        embed.set_thumbnail(url="https://img.icons8.com/?size=100&id=Qw82NJLhJoqc&format=png&color=000000")
        msg = await ctx.send(content="React to change your role color!", embed=embed)
        for role in rolecolors:
            await msg.add_reaction(rolecolors[role])           

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(AdminCommands(bot)) # add the cog to the bot