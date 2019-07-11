import asyncio
import os
import re
from urllib.parse import urlsplit

import youtube_dl
from pyrogram import Filters, Message

from merchant import BOT, db, executor, LOGS
from merchant.helpers import ReplyCheck

urlregex = re.compile(r'(?P<url>https?://[^\s]+)')
allowed_sites = ['youtu.be', 'youtube.com', 'soundcloud.com', 'i.4cdn.org', 'invidio.us', 'hooktube.com', '4cdn.com']


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


def get_data(url):
    ydl_opts = {
        'noplaylist': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(url, download=False)
        return data


async def link_handler(link, cmd, site, message: Message):
    data = get_data(link)
    await BOT.send_chat_action(
        chat_id=message.chat.id,
        action='upload_document'
    )

    key, ext = generate_key(link, cmd, data)
    value = db.get(key)

    try:
        if value:
            if 'mp3' not in cmd:
                return [value.decode(), data], ext, key
    except TypeError:
        pass

    if cmd:
        try:
            if 'mp3' in cmd and bool('youtube' in site or 'youtu.be' in site or 'hooktube' in site or 'invidio' in site):
                await BOT.send_chat_action(
                    chat_id=message.chat.id,
                    action='record_audio'
                )

                data = executor.submit(get_yt_audio, link, data, 'mp3')
                while data.done() is False:
                    await asyncio.sleep(1)
                return data.result(), 'audio', key

            elif 'audio' in cmd and bool('youtube' in site or 'youtu.be' in site or 'hooktube' in site or 'invidio' in site):
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

            else:
                raise TypeError()

        except TypeError:
            if 'audio' in cmd or 'mp3' in cmd:
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

    elif link:
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
        
        elif '4cdn.com' in link and 'webm' in link:
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
    else:
        message.continue_propagation()


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

            elif 'mp3' in cmd:
                key = key + 'audio/mp3/' + spliturl.query.split('&')[0]
                return key, 'audio'

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

            elif 'mp3' in cmd:
                key = key + 'audio/mp3/v=' + spliturl[2][1:]
                return key, 'audio'

        elif 'Music' in data['categories']:
            key = key + 'audio/v=' + spliturl[2][1:]
            return key, 'audio'

        else:
            key = key + 'video/v=' + spliturl[2][1:]
            return key, 'video'
        
    elif 'soundcloud.com' in link:
        key = 'soundcloud/' + spliturl[2][1:]
        return key, 'audio'
    
    elif '4cdn.com' in link:
        key = 'video/' + link
        return key, 'video'

    elif cmd:
        if 'audio' in cmd:
            key = 'audio/' + link
            return key, 'audio'

        elif 'get' in cmd:
            key = 'video/' + link
            return key, 'video'

        elif 'mp3' in cmd:
            key = 'audio/mp3/' + link
            return key, 'audio'


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
        filename = os.path.splitext(filename)[0] + '.mp4'
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


async def handler(bot: BOT, message: Message, link: str):
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
                        title = metadata['alt_title']
                    else:
                        title = metadata['title']

                except KeyError as e:
                    LOGS.warn(e)
                    title = ''

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
                        title=title,
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

                if 'mp3' not in ext:
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
                except AttributeError:
                    db.set(key, o.animation.file_id)

                    await BOT.send_animation(
                        chat_id=-1001496485217,
                        animation=o.animation.file_id,
                        caption=link,
                        disable_notification=True
                    )

                clean_cache(file_location, thumbnail)

    else:
        message.continue_propagation()


@BOT.on_message(Filters.regex(r'(?P<url>https?://[^\s]+)') & ~Filters.edited)
async def message_handler(bot: BOT, message: Message):
    link = urlregex.search(message.text).group('url')
    await handler(bot, message, link)


@BOT.on_message((Filters.command(commands=['get', 'audio', 'mp3']) | Filters.command(commands=['get', 'audio', 'mp3', 'mp3@videomerchantbot', 'get@videomerchantbot', 'audio@videomerchantbot'], prefix='/')) & Filters.reply & ~Filters.edited)
async def ytdl_reply(bot: BOT, message: Message):
    if urlregex.match(message.reply_to_message.text):
        link = urlregex.search(message.reply_to_message.text).group('url')
        await handler(bot, message, link)
    else:
        message.continue_propagation()
