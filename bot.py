from discord.ext import commands
import discord
import os # default module
from dotenv import load_dotenv

load_dotenv() # load all the variables from the env file
bot = commands.Bot(debug_guilds=[1056514064081231872], intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")



if __name__ == '__main__':
    if os.path.isdir("commands"):
        os.chdir("commands")
    else:
        os.chdir("commands")
    for i in os.listdir():
        if i.endswith(".py"):
            try:
                bot.load_extension(f"commands.{i[:-3]}")
            except Exception as error:
                print('{} konnte nicht geladen werden. [{}]'.format(i, error))
            else:
                print(f"{i} wurde geladen")
    if os.path.isdir("./../events"):
        os.chdir("./../events")
    else:
        os.chdir("./../events")
    for i in os.listdir():
        if i.endswith(".py"):
            try:
                bot.load_extension(f"events.{i[:-3]}")
            except Exception as error:
                print('{} konnte nicht geladen werden. [{}]'.format(i, error))
            else:
                print(f"{i} wurde geladen")

bot.run(os.getenv('TOKEN')) # run the bot with the token
