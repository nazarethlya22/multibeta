import os
import asyncio
import subprocess
import sys

from pyrogram import Filters, Message

from merchant import BOT, ADMINS

loop = asyncio.get_running_loop()


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
    proc = await loop.create_subprocess_shell(
        'ping {} -c 4'.format(ip),
        stdout=loop.subprocess.PIPE,
        stderr=loop.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    stdout = stdout.decode()
    stderr = stderr.decode()

    if stdout:
        message.reply(stdout)
    elif stderr:
        message.reply(stderr)