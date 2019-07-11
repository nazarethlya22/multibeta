from pyrogram import Filters, Message
from merchant import BOT


@BOT.on_message(Filters.regex('(?i)(trap|traps)'))
async def are_gay(bot: BOT, message: Message):
    await message.reply('Traps are fucking gay')