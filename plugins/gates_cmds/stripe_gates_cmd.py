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
from gates.aktz import stripe_gate as aktz_gate
from gates.or_gate import stripe_gate as or_gate
from gates.hoshigaki import stripe_gate as hoshigaki_gate
from gates.stripe_50c import stripe_gate as stripe_50c_gate
from gates.stripe_2d import stripe_gate as stripe_2d_gate
from gates.stripe_5d import stripe_gate as stripe_5d_gate
from time import perf_counter


GATE_CONFIG = {
    "stripe": {
        "gate_fn": aktz_gate,
        "name": "Stripe Auth",
        "amount": "$0",
        "type": "free",
    },
    "stripe1": {
        "gate_fn": or_gate,
        "name": "Stripe Charge",
        "amount": "$1",
        "type": "premium",
        "is_or_gate": True,
    },
    "stripe2": {
        "gate_fn": hoshigaki_gate,
        "name": "Stripe Billing",
        "amount": "$1",
        "type": "premium",
        "is_raw": True,
    },
    "stripe3": {
        "gate_fn": stripe_50c_gate,
        "name": "Stripe Checkout",
        "amount": "$0.50",
        "type": "premium",
    },
    "stripe4": {
        "gate_fn": stripe_2d_gate,
        "name": "Stripe Billing",
        "amount": "$2",
        "type": "premium",
    },
    "stripe5": {
        "gate_fn": stripe_5d_gate,
        "name": "Stripe Charge",
        "amount": "$5",
        "type": "premium",
    },
}


@Client.on_message(filters.command(list(GATE_CONFIG.keys()), PREFIXES))
async def stripe_gates_cmd(client: Client, m: Message):
    cmd = m.text.split()[0].lstrip("".join(PREFIXES)).lower()
    config = GATE_CONFIG.get(cmd)
    if not config:
        return

    user_id = m.from_user.id
    with Database() as db:
        if not db.is_authorized(user_id):
            return await m.reply(
                "<b>⚠️ You are not authorized. Contact the owner → @bhaskargg</b>", quote=True
            )
        user_info = db.get_info_user(user_id)
        is_free_user = user_info["MEMBERSHIP"].lower() == "free user"

        # Premium gates require credits or premium status
        if config["type"] == "premium" and is_free_user:
            if not db.user_has_credits(user_id):
                return await m.reply(
                    "<b>⚠️ You need premium or credits to use this gate.</b>", quote=True
                )

        if is_free_user:
            captcha = await anti_bots_telegram(m, client)
            if not captcha:
                return

    text = get_text_from_pyrogram(m)
    ccs = get_cc(text)
    if not ccs:
        return await m.reply(
            f"<b>Gateway:</b> <code>{config['name']} | {config['amount']}</code>\n"
            f"<b>Format:</b> <code>/{cmd} cc|month|year|cvc</code>",
            quote=True,
        )

    ini = perf_counter()
    cc, mes, ano, cvv = ccs[0], ccs[1], ccs[2], ccs[3]

    # Antispam check
    antispam_result = antispam(user_id, user_info["ANTISPAM"], is_free_user)
    if antispam_result != False:
        return await m.reply(
            f"Please wait... <code>{antispam_result}s</code>", quote=True
        )

    msg_to_edit = await m.reply("Checking...", quote=True)
    cc_formatted = f"{cc}|{mes}|{ano}|{cvv}"

    try:
        result = await config["gate_fn"](cc, mes, ano, cvv)

        # or_gate returns just a value (200 or error message string)
        if config.get("is_or_gate"):
            if result == 200:
                status = "Approved! ✅ - charged!"
                msg = f"Success - {config['amount']}"
            elif "3D" in str(result) or "requiresAction" in str(result):
                status = "Approved! ✅ - 3DS"
                msg = "3D Secure Required"
            elif "security code" in str(result).lower():
                status = "Approved! ✅ - ccn"
                msg = str(result)
            elif "insufficient funds" in str(result).lower() or "funds" in str(result).lower():
                status = "Approved! ✅ - low funds"
                msg = str(result)
            else:
                status = "Dead! ❌"
                msg = str(result) if result else "Declined"

        # hoshigaki returns a raw string
        elif config.get("is_raw"):
            raw = str(result).lower()
            if "security code" in raw:
                status = "Approved! ✅ - ccn"
            elif "funds" in raw:
                status = "Approved! ✅ - low funds"
            elif result == "" or result is None:
                status = "Approved! ✅ - charged!"
            else:
                status = "Dead! ❌"
            msg = str(result) if result else f"Success - {config['amount']}"

        # Tuple return (status, msg)
        elif isinstance(result, tuple):
            status, msg = result
        else:
            status = "Dead! ❌"
            msg = str(result) if result else "Unknown"

    except Exception as e:
        status = "Dead! ❌"
        msg = f"Error: {str(e)[:60]}"

    # Deduct credits on charge
    if "charged" in status.lower():
        with Database() as db:
            if is_free_user and db.user_has_credits(user_id):
                db.remove_credits(user_id, 1)
            db.increase_checks(user_id)
    else:
        with Database() as db:
            db.increase_checks(user_id)

    final = perf_counter() - ini

    # Get BIN info
    bin_info = await get_bin_info(cc[:6])
    if bin_info:
        brand = bin_info.get("brand", "N/A")
        card_type = bin_info.get("type", "N/A")
        level = bin_info.get("level", "N/A")
        bank = bin_info.get("bank", "N/A")
        country = bin_info.get("country_name", "N/A")
        flag = bin_info.get("country_flag", "")
    else:
        brand = card_type = level = bank = country = "N/A"
        flag = ""

    text_ = f"""<b>CC</b> - <code>{cc_formatted}</code>
<b>Status</b> - <code>{status}</code>
<b>Result</b> - <code>{msg}</code>

<b>BIN</b> - <code>{brand}</code> | <code>{card_type}</code> | <code>{level}</code>
<b>Bank</b> - <code>{bank}</code>
<b>Country</b> - <code>{country}</code> {flag}

<b>Gateway</b> - <code>{config['name']} | {config['amount']}</code>
<b>Time</b> - <code>{final:0.3}'s</code>
<b>Checked by</b> - <a href='tg://user?id={m.from_user.id}'>{m.from_user.first_name}</a>"""

    await msg_to_edit.edit(text_)
