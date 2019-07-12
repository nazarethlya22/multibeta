import os
import asyncio
import subprocess
import sys
import requests

from pyrogram import Filters, Message

from merchant import BOT, ADMINS


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


@BOT.on_message(Filters.command('ping', '!') & Filters.user(users=ADMINS))
async def ping(bot:  BOT, message: Message):
    ip = message.command[1]

    proc = await asyncio.create_subprocess_shell(
        'ping {} -c 4'.format(ip),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()
    stdout = stdout.decode()
    stderr = stderr.decode()

    if stdout:
        await message.reply(stdout)
    elif stderr:
        await message.reply(stderr)


@BOT.on_message(Filters.command('statuscode', '!') & Filters.user(users=ADMINS))
async def statuscode(bot: BOT, message: Message)
    site = message.command[1]
    r = requests.get(site)
    await message.reply(r.status_code)