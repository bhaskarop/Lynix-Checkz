from pyrogram import filters
from pyromod import Client
from pyrogram.types import Message
from utilsdf.db import Database
from utilsdf.functions import get_info_sk
from utilsdf.vars import PREFIXES
from time import perf_counter


@Client.on_message(filters.command("sk", PREFIXES))
async def sk_cmd(client: Client, m: Message):
    user_id = m.from_user.id
    with Database() as db:
        if not db.is_authorized(user_id):
            return await m.reply(
                "This chat is not approved to use this bot.", quote=True
            )
        info_user = db.get_info_user(user_id)
    ini = perf_counter()
    sk_key = m.text[len(m.command[0]) + 2 :].strip()
    if not sk_key:
        return await m.reply("Sk\nFormat - <code>/sk sk_live...</code>", quote=True)
    if not sk_key.startswith("sk_live_"):
        return await m.reply("Invalid Sk ⚠️", quote=True)
    result = await get_info_sk(sk_key)
    status = "Sk Live! ✅"
    result_msg = "Success"
    if not "available" in result:
        status = "Dead! ❌"
        result_msg = result["error"]["message"]

    text = f"""Sk - <code>{sk_key}</code>

Status - <code>{status}</code>
Result - <code>{result_msg}</code>"""

    if "available" in result:
        availableAmount = result["available"][0]["amount"]
        availableCurrency = result["available"][0]["currency"]
        pendingAmount = result["pending"][0]["amount"]
        pendingCurrency = result["pending"][0]["currency"]
        text += f"""\n
Amount - <code>{availableAmount} {availableCurrency}</code>
Pending - <code>{pendingAmount} {pendingCurrency}</code>\n"""
    final = perf_counter() - ini
    text += f"""
Time - <code>{final:0.1}'s</code>
Checked by - <a href='tg://user?id={m.from_user.id}'>{m.from_user.first_name}</a> [{info_user["RANK"].capitalize()}]"""

    text = f"<b>{text}</b>"
    await m.reply(text, quote=True)
