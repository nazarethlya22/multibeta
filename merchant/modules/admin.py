import os
import asyncio
import subprocess
import sys

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
    await message.reply("I am alive master")


@BOT.on_message(Filters.command('bash', '!') & Filters.user(users=ADMINS))
async def sh(bot:  BOT, message: Message):
    cmd = ' '.join(message.command[1:])
    print(cmd)

    proc = await asyncio.create_subprocess_shell(
        cmd,
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
