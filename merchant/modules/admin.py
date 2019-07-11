import os
import subprocess
import sys

from pyrogram import Filters, Message

from merchant import BOT, ADMINS, loop


@BOT.on_message(Filters.user(users=ADMINS) & Filters.command('update', '!'))
async def pull_update():
    subprocess.run(["git", "pull"])
    os.execl(sys.executable, sys.executable, *sys.argv)


@BOT.on_message(Filters.user(users=ADMINS) & Filters.command('restart', '!'))
async def restart():
    os.execl(sys.executable, sys.executable, *sys.argv)


@BOT.on_message(Filters.command('up', '!'))
async def up(bot: BOT, message: Message):
    message.reply("I am alive master")


@BOT.on_message(Filters.command('ping', '!'))
async def ping(bot:  BOT, message: Message):
    print(message.command)
    ip = message.command[1]
    data = await loop.subprocess_exec(['ping', ip , '-c', '4'], stdout=subprocess.PIPE)
    result = data.result().stdout
    await message.reply(result)
