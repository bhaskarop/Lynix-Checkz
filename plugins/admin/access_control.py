from pyrogram import filters
from pyromod import Client
from pyrogram.types import Message
from utilsdf.db import Database
from re import findall
from utilsdf.vars import PREFIXES
from main import CHANNEL_LOGS


@Client.on_message(filters.command("allow", PREFIXES))
async def allow_user(client: Client, m: Message):
    """Grant premium access to a user: /allow USER_ID DAYS CREDITS"""
    with Database() as db:
        if not db.is_admin(m.from_user.id):
            return
        data = m.text[len(m.command[0]) + 2 :].strip()
        data = findall(r"\d+", data)

        if len(data) < 1:
            return await m.reply(
                "<b>⚠️ Format:\n<code>/allow USER_ID</code> → 30 days, 100 credits\n<code>/allow USER_ID DAYS CREDITS</code></b>",
                quote=True,
            )

        user_id = data[0]
        days = int(data[1]) if len(data) > 1 else 30
        credits = int(data[2]) if len(data) > 2 else 100

        result = db.add_premium_membership(user_id, days, credits)
        if result is None:
            return await m.reply(
                "<b>❌ User not found! Ask them to send any message to the bot first.</b>",
                quote=True,
            )

        await m.reply(
            f"""<b>✅ Access Granted!
👤 User: <code>{user_id}</code>
📅 Days: <code>{days}</code>
💰 Credits: <code>{credits}</code>
⏳ Expires: <code>{result}</code>
</b>""",
            quote=True,
        )
        try:
            await client.send_message(
                int(user_id),
                f"<b>✅ You have been granted access!\n📅 Duration: <code>{days} days</code>\n💰 Credits: <code>{credits}</code></b>",
            )
        except Exception:
            pass
        await client.send_message(
            CHANNEL_LOGS,
            f"""#user_allowed
👤 User: <a href='tg://user?id={user_id}'>{user_id}</a>
📅 Days: <code>{days}</code>
💰 Credits: <code>{credits}</code>
👑 By: <a href='tg://user?id={m.from_user.id}'>{m.from_user.first_name}</a>""",
        )


@Client.on_message(filters.command("deny", PREFIXES))
async def deny_user(client: Client, m: Message):
    """Remove access from a user: /deny USER_ID"""
    with Database() as db:
        if not db.is_admin(m.from_user.id):
            return
        data = m.text[len(m.command[0]) + 2 :].strip()
        data = findall(r"\d+", data)

        if len(data) < 1:
            return await m.reply(
                "<b>⚠️ Format: <code>/deny USER_ID</code></b>",
                quote=True,
            )

        user_id = data[0]
        result = db.rename_premium(user_id)
        if result is None:
            return await m.reply(
                "<b>❌ User not found in database!</b>", quote=True
            )

        await m.reply(
            f"<b>🚫 Access removed for <code>{user_id}</code></b>",
            quote=True,
        )
        try:
            await client.send_message(
                int(user_id),
                "<b>🚫 Your access has been revoked.</b>",
            )
        except Exception:
            pass
        await client.send_message(
            CHANNEL_LOGS,
            f"""#user_denied
👤 User: <a href='tg://user?id={user_id}'>{user_id}</a>
👑 By: <a href='tg://user?id={m.from_user.id}'>{m.from_user.first_name}</a>""",
        )


@Client.on_message(filters.command("users", PREFIXES))
async def list_users(client: Client, m: Message):
    """List all premium/authorized users: /users"""
    with Database() as db:
        if not db.is_admin(m.from_user.id):
            return
        data = db.cursor.execute(
            f"SELECT ID, USERNAME, MEMBERSHIP, RANK, CREDITS FROM {db.BOT_TABLE} WHERE MEMBERSHIP='Premium' OR RANK IN ('admin','seller')"
        ).fetchall()

    if not data:
        return await m.reply("<b>No authorized users found.</b>", quote=True)

    text = "<b>👥 Authorized Users:\n\n</b>"
    for user in data[:30]:
        uid, uname, membership, rank, credits = user
        uname = f"@{uname}" if uname else "N/A"
        text += f"<code>{uid}</code> | {uname} | {membership} | {rank} | 💰{credits}\n"

    if len(data) > 30:
        text += f"\n<b>... and {len(data) - 30} more</b>"

    text += f"\n<b>Total: {len(data)}</b>"
    await m.reply(text, quote=True)
