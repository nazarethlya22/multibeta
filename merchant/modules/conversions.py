import asyncio
import os
import subprocess

from pyrogram import Filters, Message

from merchant import BOT
from merchant.helpers import ReplyCheck


def convert(filename, codec):
    output = os.path.splitext(filename)[0] + '.' + codec
    subprocess.run(["ffmpeg", "-i", filename, output])
    return output


@BOT.on_message(Filters.document & ~Filters.edited)
async def convert_webm(bot: BOT, message: Message):
    if 'webm' in os.path.splitext(message.document.file_name)[-1].lower():
        filename = 'cache/' + message.document.file_name
        await BOT.send_chat_action(
            chat_id=message.chat.id,
            action='record_video'
        )

        await BOT.download_media(message, file_name=filename)
        video = os.path.splitext(filename)[0] + '.' + '.mp4'
        data = await asyncio.create_subprocess_exec('ffmpeg -i {} {}'.format(filename, video))
        await data.wait()

        await BOT.send_chat_action(
            chat_id=message.chat.id,
            action='upload_video'
        )

        o = await BOT.send_video(
            chat_id=message.chat.id,
            video=video,
            disable_notification=True,
            reply_to_message_id=ReplyCheck(message)
        )

        await BOT.send_video(
            chat_id=-1001496485217,
            video=o.video.file_id,
            disable_notification=True
        )

        os.remove(filename)
        os.remove(video)

    else:
        message.continue_propagation()


@BOT.on_message(Filters.command(commands=['mp3', 'mp3@videomerchantbot'], prefix='/') & Filters.reply)
async def mp3_convert(bot: BOT, message: Message):
    if 'mp3' in os.path.splitext(message.reply_to_message.audio.file_name)[-1].lower():
        await BOT.send_message(
            chat_id=message.chat.id,
            text='File already in mp3',
            reply_to_message_id=message.message_id
        )

    try:
        if message.reply_to_message.audio.file_name:
            filename = filename = 'cache/' + message.reply_to_message.audio.file_name
    except AttributeError:
        if message.reply_to_message.document.file_name:
            filename = filename = 'cache/' + message.reply_to_message.document.file_name
    except AttributeError:
        if message.reply_to_message.video.file_name:
            filename = filename = 'cache/' + message.reply_to_message.video.file_name
    finally:
        await BOT.send_chat_action(
            chat_id=message.chat.id,
            action='record_audio'
        )
        await BOT.download_media(message.reply_to_message, file_name=filename)

        audio = os.path.splitext(filename)[0] + '.' + '.mp3'
        data = await asyncio.create_subprocess_exec('ffmpeg -i {} {}'.format(filename, audio))
        await data.wait()

        await BOT.send_chat_action(
            chat_id=message.chat.id,
            action='upload_audio'
        )

        o = await BOT.send_audio(
            chat_id=message.chat.id,
            audio=audio,
            disable_notification=True,
            reply_to_message_id=ReplyCheck(message)
        )

        await BOT.send_audio(
            chat_id=-1001496485217,
            audio=o.audio.file_id,
            disable_notification=True
        )

        os.remove(filename)
        os.remove(audio)
