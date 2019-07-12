import os
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