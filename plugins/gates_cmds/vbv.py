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
)
from utilsdf.vars import PREFIXES
from gates.vbv import vbv
from time import perf_counter


@Client.on_message(filters.command("vbv", PREFIXES))
async def vbv_2(client: Client, m: Message):
 user_id = m.from_user.id
 with Database() as db:
 if not db.is_authorized(user_id):
 return await m.reply(
 "This chat is not approved to use this bot.", quote=True
 )
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
 "Gateway <code>Vbv </code>\nFormat - <code>/vbv cc|month|year|cvc</code>",
 quote=True,
 )
 ini = perf_counter()
 cc = ccs[0]
 mes = ccs[1]
 ano = ccs[2]
 cvv = ccs[3]

 resp = await get_bin_info(cc[0:6])
 if resp is None:
 return await m.reply(
 "<b>No results found for this BIN!</b>", quote=True
 )
 brand = resp["brand"]
 country_name = resp["country_name"]
 country_flag = resp["country_flag"]
 bank = resp["bank"]
 level = resp["level"] if resp["level"] else "UNAVAILABLE"
 typea = resp["type"] if resp["type"] else "UNAVAILABLE"
 banned_bin = resp["banned"]
 rol = user_info["RANK"].capitalize()
 # nick = user_info["NICK"]
 if user_id not in [1205717709, 1115269159] and (
 banned_bin or "prepaid" in level.lower() or "prepaid" in typea.lower()
 ):
 return await m.reply("Bin - <code>Banned!</code> ⚠", quote=True)
 # check antispam
 antispam_result = antispam(user_id, user_info["ANTISPAM"], is_free_user)
 if antispam_result != False:
 return await m.reply(
 f"Please Wait... - <code>{antispam_result}'s</code>", quote=True
 )
 msg_to_edit = await m.reply("Please Wait...", quote=True)
 cc_formatted = f"{cc}|{mes}|{ano}|{cvv}"

 status, status1 = await vbv(cc, mes, ano, cvv)
 print(f"{cc}|{mes}|{ano}|{cvv} - @{m.from_user.username}")

 final = perf_counter() - ini
 with Database() as db:
 db.increase_checks(user_id)
 await msg_to_edit.edit(
 f"""<b> CC - <code>{cc_formatted}</code>
 Status - <code>{status}</code>
 Result - <code>{status1}</code>

 Bin - <code>{brand}</code> - <code>{typea}</code> - <code>{level}</code>
 Bank - <code>{bank}</code>
 Country - <code>{country_name}</code> {country_flag}

 Gateway - <code>Vbv</code>
 Time - <code>{final:0.3}'s</code>
 Checked by - <a href='tg://user?id={m.from_user.id}'>{m.from_user.first_name}</a> [{rol}]</b>"""
 )
