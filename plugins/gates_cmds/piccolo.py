from pyrogram import filters
from pyromod import Client
from pyrogram.types import Message
from utilsdf.db import Database
from utilsdf.functions import (
    get_bin_info,
    get_cc,
    antispam,
    get_text_from_pyrogram,
)
from utilsdf.vars import PREFIXES
from gates.piccolo import piccolo
from time import perf_counter


@Client.on_message(filters.command("pi", PREFIXES))
async def pi(client: Client, m: Message):
    user_id = m.from_user.id
    with Database() as db:
        if not db.is_authorized(user_id):
            return await m.reply(
                "This chat is not approved to use this bot.", quote=True
            )
        user_info = db.get_info_user(user_id)
    text = get_text_from_pyrogram(m)
    ccs = get_cc(text)
    if not ccs:
        return await m.reply(
            "Gateway <code>Piccolo - $0</code>\nFormat - <code>/pi cc|month|year|cvc</code>",
            quote=True,
        )
    ini = perf_counter()
    cc = ccs[0]
    mes = ccs[1]
    ano = ccs[2]
    cvv = ccs[3]


    # check antispam
    antispam_result = antispam(user_id, user_info["ANTISPAM"])
    if antispam_result != False:
        return await m.reply(
            f"Please Wait... - <code>{antispam_result}'s</code>", quote=True
        )
    msg_to_edit = await m.reply("Please Wait...", quote=True)
    cc_formatted = f"{cc}|{mes}|{ano}|{cvv}"

    status, status1 = await piccolo(cc, mes, ano, cvv)

    final = perf_counter() - ini
    with Database() as db:
        db.increase_checks(user_id)

    text_ = f"""<b>CC - <code>{cc_formatted}</code>
Status - <code>{status}</code>
Result - <code>{status1}</code>

Bin - <code></code> - <code></code> - <code></code>
Bank - <code></code>
Country - <code></code> 

Gateway - <code>Piccolo - $0</code>
Time - <code>{final:0.3}'s</code>
Checked by - <a href='tg://user?id={m.from_user.id}'>{m.from_user.first_name}</a> []</b>"""

    await msg_to_edit.edit(text_)
