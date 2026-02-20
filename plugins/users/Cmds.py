from pyrogram import filters
from pyromod import Client
from pyrogram.types import Message
from utilsdf.cmds_desing import text_home, buttons_cmds
from utilsdf.vars import PREFIXES


@Client.on_message(
 filters.command(
 ["cmds", "cmd", "iniciar", "inicio", "help", "menu", "gates", "gate", "start"],
 PREFIXES,
 )
)
async def cmds(client: Client, m: Message):
 user_id = m.from_user.id
 await m.reply_text(
 text=text_home.format(user_id),
 reply_markup=buttons_cmds,
 quote=True,
 )
