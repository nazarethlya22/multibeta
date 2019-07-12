import sys
import importlib
import asyncio  

from merchant.modules import ALL_MODULES
from merchant import BOT


# Load modules
for module_name in ALL_MODULES:
    imported_module = importlib.import_module("merchant.modules." + module_name)


# Asynchronous function to start the bot
async def main():
    await BOT.start()
    await BOT.idle()


if len(sys.argv) not in (1, 3, 4):
    quit(1)
else:
    asyncio.get_event_loop().run_until_complete(main())
