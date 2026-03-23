import os
import subprocess
import sys
import asyncio
import threading
from flask import Flask
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    MessageHandler, 
    CommandHandler, 
    filters, 
    ContextTypes, 
    CallbackQueryHandler
)

# --- RAILWAY 24/7 HEALTH CHECK ---
app_railway = Flask(__name__)

@app_railway.route('/')
def home():
    return "Bot is Running"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_railway.run(host='0.0.0.0', port=port)

# --- AUTO LIBRARY INSTALLER ---
def install_libs():
    libs = {'python-telegram-bot': 'telegram', 'yt-dlp': 'yt_dlp', 'flask': 'flask'}
    for lib_name, import_name in libs.items():
        try:
            __import__(import_name)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib_name, "--quiet"])

install_libs()
import yt_dlp

# --- CONFIGURATION (WITH FALLBACK) ---
# 1. Try to get from Railway Variables first
# 2. If not found, use the hardcoded string as a backup
TOKEN = os.environ.get('BOT_TOKEN') or '8595967891:AAHS1PE2om3824-l1ualhUNSQhe7MyNavVw'

OWNER_ID = 8276411342  
CREDIT_TEXT = "***Developed by [ @FUCXD ]💀***"
START_TEXT = "***Bot alive Devloper -> [ @FUCXD ]💀***"

# --- DOWNLOAD LOGIC ---
def fast_download(query):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': 's.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        'referer': 'https://www.google.com/',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if 'entries' in info:
            info = info['entries'][0]
        
        file_path = ydl.prepare_filename(info)
        title = info.get('title', 'Song')
        artist = info.get('uploader') or info.get('artist') or 'Artist'
        return file_path, title, artist

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(START_TEXT, parse_mode='Markdown', reply_to_message_id=update.message.message_id)

async def process_download(update_or_query, query, status_msg, original_msg_id):
    file_path = None
    try:
        file_path, title, artist = await asyncio.to_thread(fast_download, query)
        with open(file_path, 'rb') as audio:
            await status_msg.get_bot().send_audio(
                chat_id=status_msg.chat_id,
                audio=audio, title=title, performer=artist, 
                caption=CREDIT_TEXT, parse_mode='Markdown',
                reply_to_message_id=original_msg_id
            )
        await status_msg.delete()
    except Exception:
        try:
            await status_msg.edit_text("***❌ Error: YouTube search blocked. Try pasting a direct YouTube Link!***", parse_mode='Markdown')
        except: pass
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_text = update.message.text
    if "http" in msg_text:
        kb = [[InlineKeyboardButton("Yes ✅", callback_data=f"dl_yes|{msg_text}|{update.message.message_id}"),
               InlineKeyboardButton("No ❌", callback_data="dl_no")]]
        await update.message.reply_text("***Link detected. Download?***", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown', reply_to_message_id=update.message.message_id)
        return

    query = None
    if msg_text.lower().startswith(("/get ", "get ")):
        query = msg_text.split(None, 1)[1] if len(msg_text.split()) > 1 else None
    elif msg_text.lower().startswith(("/lr ", "lr ")):
        query = msg_text.split(None, 1)[1] if len(msg_text.split()) > 1 else None
    elif msg_text.lower().startswith("/lr"):
        query = msg_text[3:].strip() if len(msg_text) > 3 else None

    if query:
        status = await update.message.reply_text(f"***🔍 Searching for '{query}'...***", parse_mode='Markdown', reply_to_message_id=update.message.message_id)
        await process_download(update, query, status, update.message.message_id)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("dl_yes"):
        _, link, mid = q.data.split("|")
        await q.edit_message_text("***Processing...***", parse_mode='Markdown')
        s = await q.message.reply_text("***Downloading audio...***", parse_mode='Markdown')
        await process_download(q, link, s, int(mid))
    elif q.data == "dl_no":
        await q.edit_message_text("***Cancelled.***", parse_mode='Markdown')

# --- MAIN ---
async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    await app.initialize(); await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    while True: await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main())
            
