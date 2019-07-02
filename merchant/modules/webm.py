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


@BOT.on_message(Filters.document)
async def conv_webm(bot: BOT, message: Message):
    filename = 'cache/' + message.document.file_name
    if 'webm' in os.path.splitext(filename)[-1].lower():
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
    else:
        message.continue_propagation()