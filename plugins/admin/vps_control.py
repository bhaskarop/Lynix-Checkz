import os
import sys
import asyncio
import platform
import psutil
from asyncio import sleep
from pyrogram import filters
from pyromod import Client
from pyrogram.types import Message
from utilsdf.db import Database
from utilsdf.vars import PREFIXES
from datetime import datetime

START_TIME = datetime.now()


def get_uptime():
    diff = datetime.now() - START_TIME
    days = diff.days
    hours, rem = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"


def get_system_info():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return {
        "os": f"{platform.system()} {platform.release()}",
        "cpu": f"{cpu}%",
        "ram_used": f"{ram.used // (1024**2)}MB",
        "ram_total": f"{ram.total // (1024**2)}MB",
        "ram_percent": f"{ram.percent}%",
        "disk_used": f"{disk.used // (1024**3)}GB",
        "disk_total": f"{disk.total // (1024**3)}GB",
        "disk_percent": f"{disk.percent}%",
        "uptime": get_uptime(),
    }


# ── Restart Bot ──
@Client.on_message(filters.command("rbot", PREFIXES))
async def restart_bot(client: Client, m: Message):
    with Database() as db:
        if not db.is_admin(m.from_user.id):
            return
    msg = await m.reply("<b>♻️ Restarting bot...</b>", quote=True)
    await sleep(1)
    await msg.edit("<b>✅ Bot restarting... Please wait 3 seconds</b>")
    os.execl(sys.executable, sys.executable, "-B", *sys.argv)


# ── Stop Bot ──
@Client.on_message(filters.command("stopbot", PREFIXES))
async def stop_bot(client: Client, m: Message):
    with Database() as db:
        if not db.is_admin(m.from_user.id):
            return
    await m.reply("<b>🛑 Stopping bot... Use VPS to start again.</b>", quote=True)
    await sleep(1)
    os._exit(0)


# ── System Stats ──
@Client.on_message(filters.command("sys", PREFIXES))
async def system_stats(client: Client, m: Message):
    with Database() as db:
        if not db.is_admin(m.from_user.id):
            return
    msg = await m.reply("<b>📊 Fetching system info...</b>", quote=True)
    info = get_system_info()
    text = f"""<b>📊 𝙎𝙮𝙨𝙩𝙚𝙢 𝙎𝙩𝙖𝙩𝙪𝙨

⚙️ 𝙊𝙎 -» <code>{info['os']}</code>
⏱ 𝙐𝙥𝙩𝙞𝙢𝙚 -» <code>{info['uptime']}</code>

🖥 𝘾𝙋𝙐 -» <code>{info['cpu']}</code>
💾 𝙍𝘼𝙈 -» <code>{info['ram_used']}/{info['ram_total']} ({info['ram_percent']})</code>
💿 𝘿𝙞𝙨𝙠 -» <code>{info['disk_used']}/{info['disk_total']} ({info['disk_percent']})</code>
</b>"""
    await msg.edit(text)


# ── Execute Shell Command ──
@Client.on_message(filters.command("sh", PREFIXES))
async def shell_command(client: Client, m: Message):
    with Database() as db:
        if not db.is_admin(m.from_user.id):
            return
    cmd = m.text[len(m.command[0]) + 2 :].strip()
    if not cmd:
        return await m.reply(
            "<b>⚠️ Format: <code>/sh command</code></b>", quote=True
        )
    msg = await m.reply(f"<b>⚡ Running: <code>{cmd}</code></b>", quote=True)
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
        output = stdout.decode().strip() or stderr.decode().strip() or "No output"
        # Telegram message limit is 4096 chars
        if len(output) > 3500:
            output = output[:3500] + "\n\n... (truncated)"
        await msg.edit(
            f"<b>⚡ Command: <code>{cmd}</code>\n\n📤 Output:</b>\n<code>{output}</code>"
        )
    except asyncio.TimeoutError:
        await msg.edit(f"<b>⚠️ Command timed out (60s): <code>{cmd}</code></b>")
    except Exception as e:
        await msg.edit(f"<b>❌ Error: <code>{e}</code></b>")


# ── Reboot VPS ──
@Client.on_message(filters.command("reboot", PREFIXES))
async def reboot_vps(client: Client, m: Message):
    with Database() as db:
        if not db.is_admin(m.from_user.id):
            return
    await m.reply("<b>🔄 Rebooting VPS... Bot will come back in ~30s</b>", quote=True)
    await sleep(1)
    os.system("sudo reboot")


# ── Speedtest ──
@Client.on_message(filters.command("speed", PREFIXES))
async def speedtest(client: Client, m: Message):
    with Database() as db:
        if not db.is_admin(m.from_user.id):
            return
    msg = await m.reply("<b>🚀 Running speedtest...</b>", quote=True)
    try:
        process = await asyncio.create_subprocess_shell(
            "speedtest-cli --simple",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
        output = stdout.decode().strip() or stderr.decode().strip()
        if not output or "error" in output.lower():
            output = "speedtest-cli not installed.\nRun: /sh sudo apt install speedtest-cli -y"
        await msg.edit(f"<b>🚀 𝙎𝙥𝙚𝙚𝙙𝙩𝙚𝙨𝙩 𝙍𝙚𝙨𝙪𝙡𝙩\n\n<code>{output}</code></b>")
    except asyncio.TimeoutError:
        await msg.edit("<b>⚠️ Speedtest timed out</b>")
    except Exception as e:
        await msg.edit(f"<b>❌ Error: <code>{e}</code></b>")


# ── Ping ──
@Client.on_message(filters.command("ping", PREFIXES))
async def ping(client: Client, m: Message):
    start = datetime.now()
    msg = await m.reply("<b>🏓 Pong!</b>", quote=True)
    diff = (datetime.now() - start).microseconds / 1000
    await msg.edit(f"<b>🏓 Pong! <code>{diff:.2f}ms</code>\n⏱ Uptime: <code>{get_uptime()}</code></b>")
