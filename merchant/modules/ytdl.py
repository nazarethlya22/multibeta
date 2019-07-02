import youtube_dl
import asyncio
from pyrogram import Filters, Message
from urllib.parse import urlsplit
import os
import re

from merchant import BOT, db, executor, LOGS
from merchant.helpers import ReplyCheck


urlregex = re.compile(r'(?P<url>https?://[^\s]+)')
allowed_sites = ['youtu.be', 'youtube.com', 'soundcloud.com', 'i.4cdn.org', 'invidio.us', 'hooktube.com']


def site_allowed(link):
    for allowed_site in allowed_sites:
        if allowed_site in link:
            return allowed_site

    else:
        return None


def get_cmds(cmd):
    if 'get' in cmd:
        return 'get'

    elif 'audio' in cmd:
        return 'audio'

    elif 'mp3' in cmd:
        return 'mp3'

    else:
        return None


def getData(url):
    ydl_opts = {
        'noplaylist': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(url, download=False)

        return data


async def link_handler(link, cmd, site, message: Message):
    data = getData(link)
    await BOT.send_chat_action(
        chat_id=message.chat.id,
        action='upload_document'
    )

    key, ext = generate_key(link, cmd, data)
    value = db.get(key)

    if value is not None:
        return [value.decode(), data], ext, key

    if cmd:
        if 'audio' in cmd and bool('youtube' in site or 'youtu.be' in site or 'hooktube' in site or 'invidio' in site):
            await BOT.send_chat_action(
                chat_id=message.chat.id,
                action='record_audio'
            )

            data = executor.submit(get_yt_audio, link, data)
            while data.done() is False:
                await asyncio.sleep(1)

            return data.result(), 'audio', key

        elif 'get' in cmd and bool('youtube' in site or 'youtu.be' in site or 'hooktube' in site or 'invidio' in site):
            await BOT.send_chat_action(
                chat_id=message.chat.id,
                action='record_video'
            )

            data = executor.submit(get_yt_video, link, data)
            while data.done() is False:
                await asyncio.sleep(1)

            return data.result(), 'video', key
        
        elif 'audio' in cmd:
            await BOT.send_chat_action(
                chat_id=message.chat.id,
                action='record_audio'
            )

            data = executor.submit(get_audio, link, data)
            while data.done() is False:
                await asyncio.sleep(1)

            return data.result(), 'audio', key
        
        elif 'get' in cmd:
            await BOT.send_chat_action(
                chat_id=message.chat.id,
                action='record_video'
            )

            data = executor.submit(get_video, link, data)
            while data.done() is False:
                await asyncio.sleep(1)

            return data.result(), 'video', key

    else:
        if 'Music' in data['categories']:
            await BOT.send_chat_action(
                chat_id=message.chat.id,
                action='record_audio'
            )

            data = executor.submit(get_yt_audio, link, data)
            while data.done() is False:
                await asyncio.sleep(1)

            return data.result(), 'audio', key

        elif 'youtube' in site or 'hooktube' in site or 'invidio' in site or 'youtu.be' in site:
            await BOT.send_chat_action(
                chat_id=message.chat.id,
                action='record_video'
            )

            data = executor.submit(get_yt_video, link, data)
            while data.done() is False:
                await asyncio.sleep(1)

            return data.result(), 'video', key
            
        else:
            await BOT.send_chat_action(
                chat_id=message.chat.id,
                action='record_video'
            )

            data = executor.submit(get_video, link, data)
            while data.done() is False:
                await asyncio.sleep(1)

            return data.result(), 'video', key


def generate_key(link, cmd, data):
    spliturl = urlsplit(link)
    if 'youtube.com' in link or 'hooktube.com' in link or 'invidio.us' in link:
        key = 'youtube/'
        if cmd:
            if 'audio' in cmd:
                key = key + 'audio/' + spliturl.query.split('&')[0]
                return key, 'audio'

            elif 'get' in cmd:
                key = key + 'video/' + spliturl.query.split('&')[0]
                return key, 'video'

        elif 'Music' in data['categories']:
            key = key + 'audio/' + spliturl.query.split('&')[0]
            return key, 'audio'

        else:
            key = key + 'video/' + spliturl.query.split('&')[0]
            return key, 'video'

    elif 'youtu.be' in link:
        key = 'youtube/'
        if cmd:
            if 'audio' in cmd:
                key = key + 'audio/v=' + spliturl[2][1:]
                return key, 'audio'

            elif 'get' in cmd:
                key = key + 'video/v=' + spliturl[2][1:]
                return key, 'video'

        elif 'Music' in data['categories']:
            key = key + 'audio/v=' + spliturl[2][1:]
            return key, 'audio'
        else:
            key = key + 'video/v=' + spliturl[2][1:]
            return key, 'video'
        
    elif 'soundcloud.com' in link:
        key = 'soundcloud/' + spliturl[2][1:]
        return key, 'audio'

    elif cmd:
        if 'audio' in cmd:
            key = 'audio/' + link
            return key, 'audio'
        elif 'get' in cmd:
            key = 'video/' + link
            return key, 'video'


def get_yt_audio(url, data=None, codec='opus'):
    opus_opts = {
        'format': 'bestaudio',
        'outtmpl': 'cache/audio/%(title)s.%(ext)s',
        'noplaylist': True,
        'restrictfilenames': True,
        'writethumbnail': True,
        'youtube_include_dash_manifest': False,
        'max_filesize': 1500000000,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': codec,
        },
        {'key': 'FFmpegMetadata'},
        ],
    }
    with youtube_dl.YoutubeDL(opus_opts) as ydl:
        if data is None:
            data = ydl.extract_info(url, download=False)
        ydl.download([url])
        filename = ydl.prepare_filename(data)
        filename = os.path.splitext(filename)[0] + '.' + codec

        return [filename, data]


def get_yt_video(url, data=None):
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': 'cache/video/%(id)s.%(ext)s',
        'noplaylist': True,
        'youtube_include_dash_manifest': False,
        'writethumbnail': True,
        'restrictfilenames': True,
        'max_filesize': 1500000000,
        'postprocessors': [
            {'key': 'FFmpegMetadata'},
        ]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        if data is None:
            data = ydl.extract_info(url, download=False)
        ydl.download([url])
        filename = ydl.prepare_filename(data)

        return [filename, data]


def get_video(url, data=None):
    ydl_opts = {
    'outtmpl': 'cache/video/%(id)s.%(ext)s',
    'noplaylist': True,
    'nocheckcertificate': True,
    'restrictfilenames': True,
    'max_filesize': 1000000000,
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',
    }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        if data is None:
            data = ydl.extract_info(url, download=False)
        ydl.download([url])
        filename = ydl.prepare_filename(data)
        filename = os.path.splitext(filename)[0] + '.mp4'

        return [filename, data]


def get_audio(url, data=None, codec='mp3'):
    ydl_opts = {
        'outtmpl': 'cache/audio/%(title)s.%(ext)s',
        'noplaylist': True,
        'restrictfilenames': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': codec,
            'preferredquality': '0',
        },
        {'key': 'FFmpegMetadata'},
        ],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        if data is None:
            data = ydl.extract_info(url, download=False)
        ydl.download([url])
        filename = ydl.prepare_filename(data)
        filename = os.path.splitext(filename)[0] + '.' + codec

        return [filename, data]


def clean_cache(location: str, thumbnail: str):
    try:
        if os.path.exists(location):
            os.remove(location)

        if os.path.exists(thumbnail):
            os.remove(thumbnail)

    except TypeError as e:
        LOGS.warning(e)


@BOT.on_message(Filters.regex(r'(?P<url>https?://[^\s]+)') & ~Filters.edited)
async def message_handler(bot: BOT, message: Message):
    link = urlregex.search(message.text).group('url')
    cmd = get_cmds(message.text.lower().split(' ')[0])
    site = site_allowed(link)

    if cmd or site:
        if cmd:
            data, ext, key = await link_handler(link, cmd, site, message)

        elif site:
            data, ext, key = await link_handler(link, cmd, site, message)

        file_location = data[0]

        if file_location:
            metadata = data[1]
            thumbnail = os.path.splitext(file_location)[0] + '.jpg'

            try:
                if os.path.getsize(thumbnail) > 200 * 1024:
                    thumbnail = None

            except FileNotFoundError:
                thumbnail = None

            if 'audio' in ext:
                try:
                    if metadata['alt_title']:
                        tiitel = metadata['alt_title']
                    else:
                        tiitel = metadata['title']

                except KeyError as e:
                    LOGS.warn(e)
                    tiitel = ''

                await BOT.send_chat_action(
                    chat_id=message.chat.id,
                    action='upload_audio'
                )

                try:
                    o = await BOT.send_audio(
                        chat_id=message.chat.id,
                        audio=file_location,
                        performer=metadata['creator'],
                        duration=metadata['duration'],
                        title=tiitel,
                        thumb=thumbnail,
                        disable_notification=True,
                        reply_to_message_id=ReplyCheck(message)
                    )

                except KeyError as e:
                    LOGS.warn(e)
                    o = await BOT.send_audio(
                        chat_id=message.chat.id,
                        audio=file_location,
                        disable_notification=True,
                        reply_to_message_id=ReplyCheck(message)
                    )

                db.set(key, o.audio.file_id)
                clean_cache(file_location, thumbnail)

                await BOT.send_audio(
                    chat_id=-1001496485217,
                    audio=o.audio.file_id,
                    caption=link,
                    disable_notification=True
                )
                
            elif 'video' in ext:
                await BOT.send_chat_action(
                    chat_id=message.chat.id,
                    action='upload_video'
                )

                try:
                    o = await BOT.send_video(
                        chat_id=message.chat.id,
                        video=file_location,
                        duration=metadata['duration'],
                        disable_notification=True,
                        thumb=thumbnail,
                        reply_to_message_id=ReplyCheck(message)
                    )

                except KeyError as e:
                    LOGS.warn(e)

                    o = await BOT.send_video(
                        chat_id=message.chat.id,
                        video=file_location,
                        disable_notification=True,
                        reply_to_message_id=ReplyCheck(message)
                    )
                try:
                    db.set(key, o.video.file_id)

                    await BOT.send_video(
                        chat_id=-1001496485217,
                        video=o.video.file_id,
                        caption=link,
                        disable_notification=True
                    )
                except AttributeError as e:
                    LOGS.warn(e)
                    db.set(key, o.animation.file_id)

                    await BOT.send_animation(
                        chat_id=-1001496485217,
                        animation=o.animation.file_id,
                        caption=link,
                        disable_notification=True
                    )

                clean_cache(file_location, thumbnail)