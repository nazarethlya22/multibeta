import asyncio
from pyrogram import Filters, Message

from merchant import BOT
from merchant.helpers import ReplyCheck

from mediawiki import MediaWiki

osrs = MediaWiki(url='https://oldschool.runescape.wiki/api.php')


def osrswiki(search_string):
    search = osrs.search(search_string)
    page = osrs.page(search[0])
    sections = ''
    for section in page.sections:
        sections = '{}\n{}\n{}'.format(sections, section, page.section(section))
    
    text = '**{}**\n\n{}\n{}\n**Read more at:** [{}]({})'.format(page.title, page.summary, sections, page.title, page.url)
    return text


@BOT.on_message(Filters.command("oswiki", "/"))
async def wiki(bot: BOT, message: Message):
    topic = message.text.replace("/oswiki ", "")
    summary = osrswiki(topic)

    await BOT.send_message(
        chat_id=message.chat.id,
        text=summary,
        disable_notification=True,
        reply_to_message_id=ReplyCheck(message)
    )