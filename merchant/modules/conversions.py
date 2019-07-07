import os
import asyncio
import subprocess

from pyrogram import Filters, Message

from merchant import BOT, db, executor, LOGS
from merchant.helpers import ReplyCheck


def webm_to_mp4(webm):
    output = os.path.splitext(webm)[0] + '.mp4'
    subprocess.run(["ffmpeg", "-i", webm, output])
    return output


def audio_to_mp3(audio):
    output = os.path.splitext(audio)[0] + '.mp3'
    subprocess.run(["ffmpeg", "-i", audio, output])
    return output


@BOT.on_message(Filters.document & ~Filters.edited)
async def conv_file(bot: BOT, message: Message):
    if 'webm' in os.path.splitext(message.document.file_name)[-1].lower():
        filename = 'cache/' + message.document.file_name
        await BOT.send_chat_action(
            chat_id=message.chat.id,
            action='record_video'
        )

        await BOT.download_media(message, file_name=filename)
        output = executor.submit(webm_to_mp4, filename)
        video = output.result()

        while output.done() is False:
            await asyncio.sleep(1)

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

    elif 'mp3' in message.text and message.reply_to_message.document.file_name \
        and 'mp3' not in os.path.splitext(message.reply_to_message.audio.file_name)[-1].lower():
        filename = filename = 'cache/' + message.reply_to_message.document.file_name
        await BOT.send_chat_action(
            chat_id=message.chat.id,
            action='record_audio'
        )

        await BOT.download_media(message, file_name=filename)
        output = executor.submit(audio_to_mp3, filename)
        audio = output.result()

        while output.done() is False:
            await asyncio.sleep(1)

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

    elif 'mp3' in os.path.splitext(message.reply_to_message.audio.file_name)[-1].lower():
        await BOT.send_message(
            chat_id=message.chat.id,
            text='File already in mp3',
            reply_to_message_id=message.message_id
        )
        
    else:
        message.continue_propagation()