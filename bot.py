import json
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8999021234:AAFjCt8bSHKiMlkChAtyvohn1eoVqP3CTDw"
ADMIN_ID = 6994157864  # O'zingizning Telegram ID'ingiz

JSON_FILE = "videos.json"

# /add dan keyin qaysi admin qaysi kod uchun video yuborishini kutmoqda
waiting = {}


def load():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


videos = load()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot ishlayapti.")


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) != 1:
        await update.message.reply_text(
            "Foydalanish:\n/add A001"
        )
        return

    code = context.args[0].upper()

    waiting[update.effective_user.id] = code

    await update.message.reply_text(
        f"{code} uchun videoni yuboring."
    )


async def receive_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if update.effective_user.id not in waiting:
        await update.message.reply_text(
            "Avval /add KOD yozing."
        )
        return

    code = waiting[update.effective_user.id]

    file_id = update.message.video.file_id

    videos[code] = file_id
    save(videos)

    del waiting[update.effective_user.id]

    await update.message.reply_text(
        f"✅ {code} saqlandi."
    )


async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.upper()

    if text in videos:
        await update.message.reply_video(videos[text])
    else:
        await update.message.reply_text("Kod topilmadi.")


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) != 1:
        await update.message.reply_text(
            "/delete KOD"
        )
        return

    code = context.args[0].upper()

    if code in videos:
        del videos[code]
        save(videos)
        await update.message.reply_text("O'chirildi.")
    else:
        await update.message.reply_text("Topilmadi.")


async def list_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not videos:
        await update.message.reply_text("Bo'sh.")
        return

    txt = "\n".join(videos.keys())

    await update.message.reply_text(txt)


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("delete", delete))
app.add_handler(CommandHandler("list", list_codes))

app.add_handler(MessageHandler(filters.VIDEO, receive_video))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_video))

print("Bot ishga tushdi...")
app.run_polling()
