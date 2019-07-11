import requests
import asyncio
import re

from pyrogram import Filters, Message

from merchant import BOT, THECATAPI
from merchant.helpers import ReplyCheck


def get_kot(mime_types):
    headers = {"x-api-key": THECATAPI}
    r = requests.get(
        "https://api.thecatapi.com/v1/images/search?mime_types={}".format(mime_types),
        headers=headers,
    )
    if r.status_code == 200:
        data = r.json()
        url = data[0]["url"]
        return url


@BOT.on_message(Filters.regex("(?i)(post|get|send) (kot|kitten|kots|cat|cats|🐱|🐈|😸|🐱) (gif|gifs)") & ~Filters.edited)
async def post_kot_gif(bot: BOT, message: Message):
    if re.match("(?i)(post|get|send) (kot|kitten|kots|cat|cats|🐱|🐈|😸|🐱) (gif|gifs)", message.text):
        kot_gif = get_kot(mime_types="gif")
        await BOT.send_animation(
            chat_id=message.chat.id,
            animation=kot_gif,
            reply_to_message_id=ReplyCheck(message),
            disable_notification=True
        )


@BOT.on_message(Filters.regex("(?i)(post|get|send) (kot|kitten|kots|cat|cats|🐱|🐈|😸|🐱)") & ~Filters.edited)
async def post_kot(bot: BOT, message: Message):
    if re.match("(?i)(post|get|send) (kot|kitten|kots|cat|cats|🐱|🐈|😸|🐱)", message.text):
        kot_link = get_kot(mime_types="jpg,png")
        await BOT.send_photo(
            chat_id=message.chat.id,
            photo=kot_link,
            reply_to_message_id=ReplyCheck(message),
            disable_notification=True
        )