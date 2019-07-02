from pyrogram import Filters, Message
import subprocess
import asyncio
import os
import sys

from merchant import BOT, ADMINS


@BOT.on_message(Filters.user(users=ADMINS) & Filters.command('update', '!'))
async def pull_update(bot: BOT, message: Message):
    subprocess.run(["git", "pull"])
    os.execl(sys.executable, sys.executable, *sys.argv)