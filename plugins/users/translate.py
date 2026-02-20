from pyrogram import filters
from pyromod import Client
from pyrogram.types import Message
from utilsdf.db import Database
from utilsdf.functions import get_text_from_pyrogram, antispam, translate, Languages
from utilsdf.vars import PREFIXES
from pyrogram.errors.exceptions.bad_request_400 import EntityBoundsInvalid

text_example = """<b>
Example: <code>/tr es hello</code>

English - <code>en</code> 🇺🇸
Spanish - <code>es</code> 🇪🇸
Portugues - <code>pt</code> 🇧🇷
Chinesse - <code>ch</code> 🇨🇳
Russian - <code>ru</code> 🇷🇺
German - <code>de</code> 🇩🇪
Japanesse - <code>ja</code> 🇯🇵</b>"""


@Client.on_message(filters.command("tr", PREFIXES))
async def translate_cmd(client: Client, m: Message):
    user_id = m.from_user.id
    with Database() as db:
        if not db.is_authorized(user_id):
            return await m.reply(
                "This chat is not approved to use this bot.", quote=True
            )
        user_info = db.get_info_user(user_id)
        is_free_user = user_info["MEMBERSHIP"]
        is_free_user = is_free_user.lower() == "free user"

    text = get_text_from_pyrogram(m, True)
    text = text.split(" ", maxsplit=1)
    if len(text) != 2:
        return await m.reply(text_example, quote=True)
    language_code = text[0].lower().strip()
    if language_code == "ch":
        language_code = "zh-CN"
    language = next(
        (key for key, value in Languages.items() if value == language_code), None
    )
    if language_code not in list(Languages.values()):
        return await m.reply(text_example, quote=True)

    text_to_translate = text[1]
    if len(text_to_translate) <= 2:
        return await m.reply(text_example, quote=True)
    antispam_result = antispam(user_id, 4, is_free_user)
    if antispam_result != False:
        return await m.reply(
            f"Please Wait... - <code>{antispam_result}'s</code>", quote=True
        )
    try:
        await m.reply(
            f"""<b>
Lang - {language.lower().capitalize()}
Text - <code>{await translate(text_to_translate, language_code)}</code>
    </b>""",
            quote=True,
        )
    except EntityBoundsInvalid:
        await m.reply("<b>Enter a valid text!</b>", quote=True)
