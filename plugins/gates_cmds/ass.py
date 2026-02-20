from pyrogram import filters
from pyromod import Client
from pyrogram.types import Message
from utilsdf.db import Database
from utilsdf.functions import (
    anti_bots_telegram,
    get_bin_info,
    get_cc,
    antispam,
    get_text_from_pyrogram,
    user_not_premium,
)
from utilsdf.vars import PREFIXES
from gates.ass import ass
from time import perf_counter


@Client.on_message(filters.command("ass", PREFIXES))
async def ass_(client: Client, m: Message):
    user_id = m.from_user.id
    with Database() as db:
        if not db.is_premium(user_id):
            await user_not_premium(m)
            return
        user_info = db.get_info_user(user_id)
        is_free_user = user_info["MEMBERSHIP"]
        is_free_user = is_free_user.lower() == "free user"
        if is_free_user:
            captcha = await anti_bots_telegram(m, client)
            if not captcha:
                return
    text = get_text_from_pyrogram(m)
    ccs = get_cc(text)
    if not ccs:
        return await m.reply(
            "Gateway <code>Ass - $4 - vbv</code>\nFormat - <code>/ass cc|month|year|cvc</code>",
            quote=True,
        )
    ini = perf_counter()
    cc = ccs[0]
    mes = ccs[1]
    ano = ccs[2]
    cvv = ccs[3]


    # check antispam
    antispam_result = antispam(user_id, user_info["ANTISPAM"], is_free_user)
    if antispam_result != False:
        return await m.reply(
            f"Please Wait... - <code>{antispam_result}'s</code>", quote=True
        )
    msg = await m.reply("Please Wait...", quote=True)
    cc_formatted = f"{cc}|{mes}|{ano}|{cvv}"

    status, response, vbv = await ass(cc, mes, ano, cvv)

    final = perf_counter() - ini
    with Database() as db:
        db.increase_checks(user_id)

    text_ = f"""<b>CC - <code>{cc_formatted}</code>
Status - <code>{status}</code>
Result - <code>{response}</code>
Vbv - <code>{vbv}</code>

Bin - <code></code> - <code></code> - <code></code>
Bank - <code></code>
Country - <code></code> 

Gateway - <code>Ass - $4</code>
Time - <code>{final:0.3}'s</code>
Checked by - <a href='tg://user?id={m.from_user.id}'>{m.from_user.first_name}</a> []</b>"""

    await msg.edit(text_)
