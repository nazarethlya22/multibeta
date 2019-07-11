from pyrogram import Filters, Message

from merchant import BOT
from merchant.helpers import ReplyCheck

from mediawiki import MediaWiki

supported_langs = ['en', 'et', 'fr', 'nl', 'se', 'cz', 'it', 'ru', 'lv', 'lt', 'fi', 'de', 'pl', 'pt', 'es']


def wikipedia_summary(topic, lang='en'):
    wikipedia = MediaWiki(lang=lang)
    search = wikipedia.search(topic)
    page = wikipedia.page(search[0])
    text = '**{}**\n\n{}\n**Read more at:** [{}]({})'.format(page.title, page.summary, page.title, page.url)
    return text


@BOT.on_message(Filters.command("wiki", "/") & ~Filters.edited)
async def wiki(bot: BOT, message: Message):
    if len(message.command[1]) == 2:
        for lang in supported_langs:
            if lang in message.command[1].lower():
                topic = ' '.join(message.command[2:])
                lang = lang
                break
    else:
        topic = ' '.join(message.command[1:])
        lang = 'en'

    summary = wikipedia_summary(topic, lang)

    await BOT.send_message(
        chat_id=message.chat.id,
        text=summary,
        disable_notification=True,
        reply_to_message_id=ReplyCheck(message),
    )