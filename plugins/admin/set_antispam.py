from pyrogram import filters
from pyromod import Client
from pyrogram.types import Message
from utilsdf.db import Database
from re import findall
from utilsdf.vars import PREFIXES


FORMAT_CMD = "<b>Format: <code>/antispam USER_ID ANTISPAM</code></b>"


@Client.on_message(filters.command("antispam", PREFIXES))
async def spam(client: Client, m: Message):
    user_id = m.from_user.id
    with Database() as db:
        if not db.is_admin(user_id):
            return
        text = m.text[len(m.command[0]) + 2 :].strip()
        data_nums = findall(r"\d+", text)
        if len(data_nums) != 2:
            return await m.reply(FORMAT_CMD, quote=True)
        id = data_nums[0]
        antispam = data_nums[1]
        result = db.set_antispam(id, antispam)
        if result is None:
            return await m.reply(
                "<b>The ID is not found in the database!\nAsk the user to talk to the bot!</b>",
                quote=True,
            )
        await m.reply(
            f"""<b>
The ID <code>{id}</code> now has <code>{antispam}</code> antispam
</b>""",
            quote=True,
        )
