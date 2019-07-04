from pyrogram import Filters, Message
import subprocess
import asyncio
import os
import sys

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


@BOT.on_message(Filters.command('uptime', '!'))
async def uptime(bot:  BOT, message: Message):
    pass