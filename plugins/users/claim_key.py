from pyrogram import filters
from pyromod import Client
from pyrogram.types import Message
from utilsdf.db import Database
from utilsdf.vars import PREFIXES
from main import CHANNEL_LOGS


@Client.on_message(filters.command("claim", PREFIXES))
async def claim(client: Client, m: Message):
    key = m.text[len(m.command[0]) + 2 :].strip()
    if not key or not key.startswith("key-aktz"):
        return await m.reply("<b>Enter a valid key!</b>", quote=True)
    user_id = m.from_user.id
    with Database() as db:
        if db.is_seller(user_id):
            return await m.reply(
                "<b>Sellers cannot claim keys. Lynix Checker ⚡</b>",
                quote=True,
            )
        result = db.claim_key(key, user_id)
    if result is None:
        return await m.reply(
            "<b>The key <code>{}</code> is not found in my database!</b>".format(
                key
            ),
            quote=True,
        )
    await m.reply(
        f"""<b>
The key <code>{key}</code> has been claimed successfully!
Expiration: <code>{result}</code>

</b>""",
        quote=True,
    )
    await client.send_message(
        CHANNEL_LOGS,
        f"""#key_claimed
id - <code>{user_id}</code>
key -  <code>{key}</code>
expiration - <code>{result}</code>
claimed by -  <a href='tg://user?id={m.from_user.id}'>{m.from_user.first_name}</a>""",
    )
    link = await client.create_chat_invite_link(-1001897182152, member_limit=1)
    await client.unban_chat_member(-1001897182152, user_id)
    await client.send_message(user_id, f"<b>Users Group: {link.invite_link}</b>")
