from pyrogram import filters
from pyromod import Client
from pyrogram.types import Message
from utilsdf.db import Database
from re import findall
from utilsdf.vars import PREFIXES
from main import CHANNEL_LOGS


@Client.on_message(filters.command("addp", PREFIXES))
async def addp(client: Client, m: Message):
 user_id = m.from_user.id
 with Database() as db:
 if not db.is_admin(user_id):
 return
 data = m.text[len(m.command[0]) + 2 :].strip()
 data = findall(r"\d+", data)

 if len(data) != 3:
 return await m.reply("<b>Format: ID DAYS CREDITS</b>", quote=True)

 id = data[0]
 days = data[1]

 credits = data[2]
 result = db.add_premium_membership(id, days, credits)
 info_user = db.get_info_user(user_id)
 if result is None:
 return await m.reply(
 "<b>The ID is not found in the database!\nAsk the user to run <code>/start</code></b>",
 quote=True,
 )
 await m.reply(
 f"""<b>
The ID <code>{id}</code> has been promoted to Premium plan!
Days: <code>{days}</code>
Credits: <code>{credits}</code>
Expiration: <code>{result}</code>
</b>""",
 quote=True,
 )
 await client.send_message(
 CHANNEL_LOGS,
 f"""#new_user_premium_add

id - <a href='tg://user?id={id}'>{id}</a>
days - <code>{days}</code>
credits - <code>{credits}</code>
added by - <a href='tg://user?id={user_id}'>{m.from_user.first_name}</a> [{info_user["RANK"].capitalize()}]""",
 )
 link = await client.create_chat_invite_link(-1001897182152, member_limit=1)
 await client.unban_chat_member(-1001897182152, int(id))
 await client.send_message(
 int(id), f"<b>Users Group: {link.invite_link}</b>"
 )
