import discord
from discord.ext import commands
import os

class NightclubInterface(discord.ui.Button):
    def __init__(self):
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="Approve Me!",
            custom_id="approve_button"
            )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != 327880195476422656:
            return await interaction.response.send_message("You are not the owner of the bot!", ephemeral=True)
        
        await interaction.response.send_modal(NightclubAgeVerification(title="Age Verification"))
        

class Nightclub(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot
    @commands.slash_command(name="nightclub", description="Enter the nightclub", guild_ids=[1056514064081231872])
    async def nightclub(self, ctx):
        if ctx.author.id != 327880195476422656:
            return await ctx.respond("You are not the owner of the bot!", ephemeral=True)
        view = discord.ui.View(timeout=None)
        view.add_item(NightclubInterface())

        embed = discord.Embed(
            title="Nightclub",
            description="Click the button to get approved to join the Nightclub!\r\nPlease note that this will start a manual verification process. Only click on this button if you are 18+.",
            color=discord.Color.blurple()
            )
        await ctx.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_ready(self):
        view = discord.ui.View(timeout=None)
        view.add_item(NightclubInterface())
        self.bot.add_view(view)

class NightclubAgeVerification(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            discord.ui.InputText(
                label="Enter your age",
                placeholder="Your Age",
                max_length=2,
            ),
            *args,
            **kwargs
        )
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != 327880195476422656:
            return await interaction.respond("You are not the owner of the bot!", ephemeral=True)
        if interaction.user.get_role(1229064333993050123) is not None:
            await interaction.guild.get_channel(1283842433284837396).send(f"<@&1311047394074300498>\r\n{interaction.user.mention} has requested to join the Nightclub with the <18 Role...")
            return await interaction.respond("You have the <18 Role...", ephemeral=True)
        if not self.children[0].value:
            return await interaction.response.send_message("You must enter your age!", ephemeral=True)
        elif not self.children[0].value.isnumeric():
            return await interaction.response.send_message("You must enter a valid number!", ephemeral=True)
        elif int(self.children[0].value) < 18:
            await interaction.guild.get_channel(1283842433284837396).send(f"<@&1311047394074300498>\r\n{interaction.user.mention} has requested to join the Nightclub with an **underage** of {self.children[0].value} years...")
            return await interaction.respond("Only members 18 years old or older can get approved for the Nightclub!", ephemeral=True)
        await interaction.guild.get_channel(1283842433284837396).send(f"<@&1311047394074300498>\r\n{interaction.user.mention} has requested to join the Nightclub with an age of {self.children[0].value} years.")
        await interaction.respond("Your request to the Nightclub has been forwarded to the Serverteam!", ephemeral=True)



def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Nightclub(bot)) # add the cog to the bot