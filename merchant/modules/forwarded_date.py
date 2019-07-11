from datetime import datetime

from pyrogram import Filters, Message
from merchant import BOT, LOGS


@BOT.on_message(Filters.reply & Filters.command('sentdate', '/'))
async def get_forwarded_message_date(bot: BOT, message: Message):
    original_date = datetime.utcfromtimestamp(message.reply_to_message.forward_date).strftime('%d-%m-%Y %H:%M:%S')
    await BOT.send_message(
        chat_id=message.chat.id,
        text='This message was sent: {}'.format(original_date),
        reply_to_message_id=message.reply_to_message.message_id
    )
