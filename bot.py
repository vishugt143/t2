# Don't Remove Credit @teacher_slex
# Subscribe YouTube ƈɦǟռռɛʟ For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram import filters, Client, errors
from pyrogram.errors.exceptions.flood_420 import FloodWait
from database import add_user, add_group, all_users, all_groups, users, remove_user
from configs import cfg
import asyncio

app = Client(
    "approver",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

#━━━━━━━━━━━━━━━━━━━━ HELPER ━━━━━━━━━━━━━━━━━━━━
def parse_post_link(link: str):
    parts = link.split("/")
    chat = parts[-2]
    msg_id = int(parts[-1])
    return chat, msg_id

#━━━━━━━━━━━━━━━━━━━━ JOIN REQUEST ━━━━━━━━━━━━━━━━━━━━
@app.on_chat_join_request(filters.group | filters.channel)
async def approve(_, m: Message):
    op = m.chat
    user = m.from_user
    try:
        add_group(op.id)
        await app.approve_chat_join_request(op.id, user.id)
        add_user(user.id)

        # ✅ WELCOME MESSAGE
        await app.send_message(
            user.id,
            f"👋 Welcome • {user.first_name}\n\n"
            "💸 𝐉𝐨𝐢𝐧 𝐫𝐞𝐪𝐮𝐞𝐬𝐭 𝐦𝐢𝐥 𝐠𝐚𝐲𝐢 ✅\n\n"
            "𝐀𝐏𝐊 𝐚𝐮𝐫 𝐬𝐞𝐭𝐮𝐩 𝐯𝐢𝐝𝐞𝐨 𝐧𝐢𝐜𝐡𝐞 𝐡𝐚𝐢 👇"
        )

        # 🔥 COPY APK / VIDEO FROM OTHER CHANNEL (NO FORWARD TAG)
        for link in cfg.POSTS:
            try:
                chat_id, msg_id = parse_post_link(link)
                await app.copy_message(
                    chat_id=user.id,
                    from_chat_id=chat_id,
                    message_id=msg_id
                )
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Copy failed → {link} | {e}")

    except errors.PeerIdInvalid:
        print("User ne bot start nahi kiya")
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as err:
        print(err)

#━━━━━━━━━━━━━━━━━━━━ START ━━━━━━━━━━━━━━━━━━━━
@app.on_message(filters.private & filters.command("start"))
async def op(_, m: Message):

    add_user(m.from_user.id)

    # ================= NORMAL USER =================
    if m.from_user.id not in cfg.SUDO:
        await m.reply_text(
            "𝐁𝐇𝐀𝐈 𝐇𝐀𝐂𝐊 𝐒𝐄 𝐏𝐋𝐀𝐘 𝐊𝐑𝐎\n\n"
            "💸𝐏𝐑𝐎𝐅𝐈𝐓 𝐊𝐑𝐎🍻"
        )

        # COPY POSTS (APK / VIDEO)
        for link in cfg.POSTS:
            try:
                chat_id, msg_id = parse_post_link(link)
                await app.copy_message(
                    chat_id=m.from_user.id,
                    from_chat_id=chat_id,
                    message_id=msg_id
                )
                await asyncio.sleep(1)
            except:
                pass
        return

    # ================= ADMIN DIRECT HOME (NO JOIN CHECK) =================
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("🗯 ƈɦǟռռɛʟ", url="https://t.me/lnx_store"),
            InlineKeyboardButton("💬 Support", url="https://t.me/teacher_slex")
        ]]
    )

    await m.reply_photo(
        photo="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhsaR6kRdTPF2ZMEgmgSYjjXU6OcsJhkBe1EWtI1nfbOziINTYzxjlGCMSVh-KoH05Z8MpRWhVV9TIX_ykpjdeGqJ1atXy1TUqrVkohUxlykoZyl67EfMQppHoWYrdHmdi6FMcL9v-Vew2VtaWHWY_eGZt-GN057jLGvYj7UV49g0rXVxoDFXQAYxvaX1xP/s1280/75447.jpg",
        caption=(
            f"**🦊 Hello {m.from_user.mention}!**\n\n"
            f"I'm an auto approve bot.\n"
            f"I can approve users in Groups / ƈɦǟռռɛʟs.\n\n"
            f"📢 Broadcast : /bcast\n"
            f"📊 Users : /users\n\n"
            f"__Powered By : @teacher_slex__"
        ),
        reply_markup=keyboard
    )
#━━━━━━━━━━━━━━━━━━━━ USERS COUNT ━━━━━━━━━━━━━━━━━━━━
@app.on_message(filters.command("users") & filters.user(cfg.SUDO))
async def dbtool(_, m: Message):
    xx = all_users()
    x = all_groups()
    await m.reply_text(
        f"🙋‍♂️ Users : `{xx}`\n👥 Groups : `{x}`\n📊 Total : `{xx + x}`"
    )

#━━━━━━━━━━━━━━━━━━━━ BROADCAST COPY ━━━━━━━━━━━━━━━━━━━━
@app.on_message(filters.command("bcast") & filters.user(cfg.SUDO))
async def bcast(_, m: Message):
    lel = await m.reply("⚡ Broadcasting...")
    success = failed = 0

    for u in users.find():
        try:
            await m.reply_to_message.copy(u["user_id"])
            success += 1
        except:
            failed += 1

    await lel.edit(f"✅ Success: `{success}`\n❌ Failed: `{failed}`")

#━━━━━━━━━━━━━━━━━━━━ BROADCAST FORWARD ━━━━━━━━━━━━━━━━━━━━
@app.on_message(filters.command("fcast") & filters.user(cfg.SUDO))
async def fcast(_, m: Message):
    lel = await m.reply("⚡ Forwarding...")
    success = failed = 0

    for u in users.find():
        try:
            await m.reply_to_message.forward(u["user_id"])
            success += 1
        except:
            failed += 1

    await lel.edit(f"✅ Success: `{success}`\n❌ Failed: `{failed}`")

print("🤖 Bot is Alive!")
app.run()
