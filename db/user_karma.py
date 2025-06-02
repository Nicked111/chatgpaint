import logging

from sqlalchemy import insert, select, delete

from db import Database
from db.tables import KarmaTable, RewardsTable


class UserKarma(Database):

    async def create_user_record_in_karma(self, user_id, guild_id):
        async with self.get_session() as session:
            existing_record = await session.execute(
                select(KarmaTable).where(KarmaTable.user_id == user_id, KarmaTable.guild_id == guild_id))
            if existing_record.scalars().first():
                logging.error(f"User record already exists for user_id={user_id}, guild_id={guild_id}")
                return

            insert_stmt = insert(KarmaTable).values(user_id=user_id, guild_id=guild_id, karma=0)
            await session.execute(insert_stmt)
            await session.commit()
            logging.info(f"Created new karma record for user_id={user_id}, guild_id={guild_id}")

    async def adjust_karma_for_user(self, user_id, guild_id, amount: int):
        async with self.get_session() as session:
            record = await session.get(KarmaTable, {"user_id": user_id, "guild_id": guild_id})

            if record:
                record.karma += amount
            else:
                record = KarmaTable(user_id=user_id, guild_id=guild_id, karma=+amount)
                session.add(record)

            await session.commit()

    async def get_karma_leaderboard(self, guild_id, limit: int = 10):
        async with self.get_session() as session:
            result = await session.execute(
                select(KarmaTable).where(KarmaTable.guild_id == guild_id).order_by(KarmaTable.karma.desc()).limit(
                    limit))
            return result.scalars().all()

    async def clear_karma_leaderboard(self, guild_id):
        async with self.get_session() as session:
            await session.execute(delete(KarmaTable).where(KarmaTable.guild_id == guild_id))
            await session.commit()

    async def get_user_karma(self, user_id, guild_id):
        async with self.get_session() as session:
            record = await session.get(KarmaTable, {"user_id": user_id, "guild_id": guild_id})
            if record:
                return record.karma
            else:
                await self.create_user_record_in_karma(user_id, guild_id)
                return 0

    async def add_reward(self, role_id, guild_id, karma_needed: int):
        async with self.get_session() as session:
            reward = RewardsTable(role_id=role_id, guild_id=guild_id, karma_needed=karma_needed)
            session.add(reward)
            await session.commit()

    async def remove_reward(self, role_id, guild_id):
        async with self.get_session() as session:
            reward = await session.get(RewardsTable, {"role_id": role_id, "guild_id": guild_id})
            if reward:
                await session.delete(reward)
                await session.commit()

    async def list_rewards(self, guild_id):
        async with self.get_session() as session:
            result = await session.execute(select(RewardsTable).where(RewardsTable.guild_id == guild_id))
            return result.scalars().all()

    async def handle_message_karma(self, user_id: int, guild_id: int, timestamp: float):
        async with self.get_session() as session:
            karma_entry = await session.get(KarmaTable, {"user_id": user_id, "guild_id": guild_id})

            if karma_entry:
                if karma_entry.timestamp_last_message < timestamp - 60:
                    karma_entry.karma += 1
                    karma_entry.timestamp_last_message = timestamp
            else:
                karma_entry = KarmaTable(user_id=user_id, guild_id=guild_id, karma=1,
                                         timestamp_last_message=int(timestamp), )
                session.add(karma_entry)

            await session.commit()

    async def handle_reaction_change(self, message_author, guild_id, emoji_id, is_addition: bool):
        upvote_emoji = 1199472652721586298
        downvote_emoji = 1199472654185418752

        if emoji_id not in {upvote_emoji, downvote_emoji}:
            logging.debug("Ignoring unrelated emoji")
            return

        try:
            amount = 0
            if emoji_id == upvote_emoji:
                amount = 1 if is_addition else -1
            elif emoji_id == downvote_emoji:
                amount = -1 if is_addition else 1

            user_karma = await UserKarma().get_user_karma(message_author.id, guild_id)

            # Only adjust karma if it makes sense
            if amount < 0 and user_karma <= 0:
                logging.debug(f"Attempted to reduce karma below 0 for User ID {message_author.id}")
                return

            await UserKarma().adjust_karma_for_user(message_author.id, guild_id, amount)
            logging.info(
                f"Karma {'added' if is_addition else 'removed'}: {amount} for User ID {message_author.id} in Guild ID {guild_id}")
        except Exception as e:
            logging.error(f"Error handling reaction change: {e}")
