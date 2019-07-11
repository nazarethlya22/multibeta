import requests

from pyrogram import Filters, Message

from merchant import BOT


text = '''
**Username:** {username}

**Overall:** {overall}
**Attack:** {attack}
**Defence:** {defence}
**Strength:** {strength}
**Hitpoints:** {hitpoints}
**Ranged:** {ranged}
**Prayer:** {prayer}
**Magic:** {magic}
**Cooking:** {cooking}
**Woodcutting:** {woodcutting}
**Fletching:** {fletching}
**Fishing:** {fishing}
**Firemaking:** {firemaking}
**Crafting:** {crafting}
**Smithing:** {smithing}
**Mining:** {mining}
**Herblore:** {herblore}
**Agility:** {agility}
**Thieving:** {thieving}
**Slayer:** {slayer}
**Farming:** {farming}
**Runecraft:** {runecraft}
**Hunter:** {hunter}
**Construction:** {construction}
'''


def osrshs(username):
    r = requests.get('https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={}'.format(username))
    if r.status_code == 200:
        data = r.content.decode()
        data = data.split('\n')

        stats = {
            'username': username,
            'overall': data[0].split(',')[1],
            'attack': data[1].split(',')[1],
            'defence': data[2].split(',')[1],
            'strength': data[3].split(',')[1],
            'hitpoints': data[4].split(',')[1],
            'ranged': data[5].split(',')[1],
            'prayer': data[6].split(',')[1],
            'magic': data[7].split(',')[1],
            'cooking': data[8].split(',')[1],
            'woodcutting': data[9].split(',')[1],
            'fletching': data[10].split(',')[1],
            'fishing': data[11].split(',')[1],
            'firemaking': data[12].split(',')[1],
            'crafting': data[13].split(',')[1],
            'smithing': data[14].split(',')[1],
            'mining': data[15].split(',')[1],
            'herblore': data[16].split(',')[1],
            'agility': data[17].split(',')[1],
            'thieving': data[18].split(',')[1],
            'slayer': data[19].split(',')[1],
            'farming': data[20].split(',')[1],
            'runecraft': data[21].split(',')[1],
            'hunter': data[22].split(',')[1],
            'construction': data[23].split(',')[1]
        }

        highscores = text.format(**stats)

        return highscores
    elif r.status_code == 404:
        return "User {} was not found".format(username)


@BOT.on_message(Filters.command('osstats', '/') & ~Filters.edited)
async def osrs_highscores(bot: BOT, message: Message):
    username = message.text.replace("/osstats ", "")
    stats = osrshs(username)
    await BOT.send_message(
        chat_id=message.chat.id,
        text=stats,
        reply_to_message_id=message.message_id
    )