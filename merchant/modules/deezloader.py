import re
import os
import asyncio

import deezloader
import mutagen

from pyrogram import Filters, Message

from merchant import BOT, executor, LOGS, DL_USERNAME, DL_PASSWORD, DL_ARL, executor
from merchant.helpers import ReplyCheck


deezer = deezloader.Login(DL_USERNAME, DL_PASSWORD, DL_ARL)

urlregex = re.compile(r'(?P<url>https?://[^\s]+)')
allowed_sites = ['open.spotify.com']


def clean_cache(location: str):
    try:
        if os.path.exists(location):
            os.remove(location)

    except TypeError as e:
        LOGS.warning(e)


def site_allowed(link):
    for allowed_site in allowed_sites:
        if allowed_site in link:
            return allowed_site
    else:
        return None


def download_track(link, quality='FLAC'):
    r = deezer.download_trackspo(link, output='cache/deezloader/', quality=quality, recursive_quality=True, recursive_download=True)
    return r


@BOT.on_message(Filters.regex(r'(?P<url>https?://[^\s]+)') & ~Filters.edited)
async def spotify_handler(bot: BOT, message: Message):
    link = urlregex.search(message.text).group('url')
    if site_allowed(link) is not None:
        r = executor.submit(download_track, link)
        while r.done() is False:
            await asyncio.sleep(1)

        result = r.result()
        metadata = mutagen.flac.Open(result)

        length = int(metadata['length'][0])
        artist = str(metadata['albumartist'][0])
        title = str(metadata['title'][0])

        await BOT.send_audio(
        chat_id=message.chat.id,
        audio=result,
        performer=artist,
        title=title,
        duration=length,
        disable_notification=True,
        reply_to_message_id=ReplyCheck(message)
        )

        clean_cache(result)
    else:
        message.continue_propagation()