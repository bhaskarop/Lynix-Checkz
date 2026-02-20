from pyrogram import filters
from pyromod import Client
from pyrogram.types import Message
from utilsdf.db import Database
from utilsdf.functions import get_text_from_pyrogram, user_not_premium
from utilsdf.vars import PREFIXES
from gates.ssh import ssh
from time import perf_counter
import re


@Client.on_message(filters.command("ssh", PREFIXES))
async def ssh(client: Client, m: Message):
    user_id = m.from_user.id
    with Database() as db:
        if not db.is_admin(user_id):
            await user_not_premium(m)
            return
        user_info = db.get_info_user(user_id)
    text = get_text_from_pyrogram(m)
    e_ = re.split(r"\||\s|:", text)
    us = e_[1] if len(e_) > 1 else None
    ps = e_[2] if len(e_) > 2 else None
    s = e_[3] if len(e_) > 3 else None

    if us == None or ps == None or s == None:
        return await m.reply(
            "Gateway <code>Ssh</code>\nFormat - <code>/ssh user password br 1</code>",
            quote=True,
        )
    ini = perf_counter()

    msg_to_edit = await m.reply("Please Wait...", quote=True)
    (
        status,
        msg,
        ip,
        host,
        us,
        ps,
        exp,
        limit,
        server,
        ssh_,
        ssl,
        websocket,
        direct,
        key_dns,
        ns_dns,
    ) = await ssh(us, ps, s)

    final = perf_counter() - ini

    rol = user_info["RANK"].capitalize()

    await msg_to_edit.edit(
        f"""<b>Status - <code>{status}</code>
Result - <code>{msg}</code>

Host - <code>{host}</code>
User - <code>{us}</code>
Pass - <code>{ps}</code>
Server - <code>{server}</code>

Ip - <code>{ip}</code>
Exp - <code>{exp}</code>
Limit - <code>{limit}</code>

Ssh - <code>{ssh_}</code>
Ssl - <code>{ssl}</code>
Websocket - <code>{websocket}</code>
Direct - <code>{direct}</code>
Key Dns - <code>{key_dns}</code>
Ns Dns - <code>{ns_dns}</code>

Gateway - <code>Ssh</code>
Time - <code>{final:0.3}'s</code>
Checked by - <a href='tg://user?id={m.from_user.id}'>{m.from_user.first_name}</a> [{rol
    }]</b>"""
    )
