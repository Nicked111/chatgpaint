import logging
import discord
from discord.ext import commands
from db.temp_voice import TempVoiceBackend
import os
from dotenv import load_dotenv

load_dotenv()


class TempVoice(commands.Cog):  # create a class for our cog that inherits from commands.Cog
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(message)s', handlers=[logging.StreamHandler()])

    def __init__(self, bot):  # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        joinToCreateVoice = int(os.getenv("JOINTOCREATEVOICE"))
        joinToCreateParent = int(os.getenv("JOINTOCREATEPARENT"))

        # Handle case when member joins a voice channel
        if self._is_joining_voice(before, after):
            if after.channel.id == joinToCreateVoice:
                await createTempVoice(self.bot, joinToCreateParent, member)
            return

        # Handle case when member leaves a voice channel
        if self._is_leaving_voice(before, after):
            await self._handle_channel_leave(before, joinToCreateParent, joinToCreateVoice)
            return

        # Handle case when member moves between voice channels
        if self._is_moving_between_channels(before, after):
            await self._handle_channel_move(before, after, joinToCreateParent, joinToCreateVoice, member)

    def _is_joining_voice(self, before, after):
        return before.channel is None and after.channel is not None

    def _is_leaving_voice(self, before, after):
        return before.channel is not None and after.channel is None

    def _is_moving_between_channels(self, before, after):
        return before.channel and after.channel

    async def _handle_channel_leave(self, before, parent_id, create_voice_id):
        if before.channel.category_id != parent_id or before.channel.id == create_voice_id:
            return

        if len(before.channel.members) == 0:
            await deleteTempVoice(self.bot, before.channel.id)

    async def _handle_channel_move(self, before, after, parent_id, create_voice_id, member):
        # Skip if neither channel is in temp category
        if not self._is_temp_channel_involved(before, after, parent_id):
            return

        # Handle moving to create-voice channel
        if after.channel.id == create_voice_id:
            if len(before.channel.members) == 0 and before.channel.category_id == parent_id:
                await deleteTempVoice(self.bot, before.channel.id)
            await createTempVoice(self.bot, parent_id, member)
            return

        # Handle leaving empty temp channel
        if before.channel.category_id == parent_id and before.channel.id != create_voice_id:
            if len(before.channel.members) == 0:
                await deleteTempVoice(self.bot, before.channel.id)

    def _is_temp_channel_involved(self, before, after, parent_id):
        return before.channel.category_id == parent_id or after.channel.category_id == parent_id


def setup(bot):  # this is called by Pycord to setup the cog
    bot.add_cog(TempVoice(bot))  # add the cog to the bot


async def createTempVoice(bot, joinToCreateParent, member):
    category = bot.get_channel(joinToCreateParent)  # get the category
    channel = await category.create_voice_channel(f"🔊・{member.display_name}'s Channel",
                                                  user_limit=10)  # create the channel with 5 slots
    await TempVoiceBackend().create_temp_voice(member.id, channel.id,
                                               member.guild.id)  # save the channel id to the database
    await member.move_to(channel)  # move the member to the channel
    return channel


async def deleteTempVoice(bot, tempVoiceId):
    channel = bot.get_channel(tempVoiceId)  # get the channel
    await channel.delete()  # delete the channel
    await TempVoiceBackend().delete_temp_voice(tempVoiceId)  # delete the channel from the database
    return channel
