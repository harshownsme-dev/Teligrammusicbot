import os
import subprocess
import sys
import asyncio
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    MessageHandler, 
    CommandHandler, 
    filters, 
    ContextTypes, 
    CallbackQueryHandler
)

# --- COLORS FOR PYDROID CONSOLE ---
GREEN = "\033[92m"
BLUE = "\033[94m"
RED = "\033[91m"
RESET = "\033[0m"

# --- SILENT INSTALLER ---
def install_libs():
    libs = {'python-telegram-bot': 'telegram', 'yt-dlp': 'yt_dlp'}
    for lib_name, import_name in libs.items():
        try:
            __import__(import_name)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib_name, "--quiet"])

install_libs()
import yt_dlp

# --- CONFIGURATION ---
TOKEN = '8595967891:AAG3yQaO4s_RddUOe1zrAkTu4yAvfMIIe2Q'
OWNER_ID = 8276411342  
CREDIT_TEXT = "***Developed by [ @FUCXD ]💀***"
START_TEXT = "***Bot alive Devloper -> [ @FUCXD ]💀***"
USER_FILE = "users.txt"

# --- USER DATABASE MANAGEMENT ---
def save_user(user_id):
    if not os.path.exists(USER_FILE):
        open(USER_FILE, "w").close()
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_users_list():
    if not os.path.exists(USER_FILE): return []
    with open(USER_FILE, "r") as f:
        return f.read().splitlines()

# --- MUSIC DOWNLOAD LOGIC ---
def fast_download(query):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': 's.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch1',
        'nocheckcertificate': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if 'entries' in info:
            info = info['entries'][0]
        
        file_path = ydl.prepare_filename(info)
        title = info.get('title', 'Song')
        artist = info.get('uploader') or info.get('artist') or 'Artist'
        return file_path, title, artist

# --- BOT COMMANDS SETTING ---
async def set_bot_commands(application: Application):
    commands = [
        BotCommand("start", "Check if bot is alive"),
        BotCommand("help", "Show help menu"),
        BotCommand("get", "Download song by name"),
        BotCommand("lr", "Search song by lyrics"),
        BotCommand("broadcast", "Dev: Message all users")
    ]
    try:
        await application.bot.delete_my_commands()
        await application.bot.set_my_commands(commands)
    except:
        pass

# --- COMMAND HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    await update.message.reply_text(START_TEXT, parse_mode='Markdown', reply_to_message_id=update.message.message_id)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "***🎵 Music Bot Help Menu***\n\n"
        "***• /help - Show this help menu***\n"
        "***• /get [name] - Download by song name***\n"
        "***• /lr [lyrics] - Search by lyrics***\n"
        "***• Paste Link - Auto-detect media links***\n\n"
        "***Dev - @FUCXD***"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_to_message_id=update.message.message_id)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    msg_to_send = " ".join(context.args)
    if not msg_to_send:
        await update.message.reply_text("***Usage: /broadcast [message]***", parse_mode='Markdown')
        return
    
    users = get_users_list()
    count = 0
    formatted_msg = f"***{msg_to_send}***"
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=int(user_id), text=formatted_msg, parse_mode='Markdown')
            count += 1
            await asyncio.sleep(0.05)
        except: continue
    await update.message.reply_text(f"***✅ Broadcast sent to {count} users.***", parse_mode='Markdown')

# --- CORE PROCESSING ---
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
        try: await status_msg.edit_text("***❌ Error: Song not found.***", parse_mode='Markdown')
        except: pass
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    msg_text = update.message.text

    if "http://" in msg_text or "https://" in msg_text:
        # We store the original message ID in the callback data to reply to it later
        keyboard = [[InlineKeyboardButton("Yes ✅", callback_data=f"dl_yes|{msg_text}|{update.message.message_id}"),
                     InlineKeyboardButton("No ❌", callback_data="dl_no")]]
        await update.message.reply_text("***Would you allow me to send the song here?***", 
                                        reply_markup=InlineKeyboardMarkup(keyboard),
                                        parse_mode='Markdown',
                                        reply_to_message_id=update.message.message_id)
        return

    query = None
    if msg_text.lower().startswith(("/get ", "get ")):
        query = msg_text.split(None, 1)[1] if len(msg_text.split()) > 1 else None
    elif msg_text.lower().startswith("/lr"):
        query = msg_text[3:].strip()

    if query:
        status_text = (
            f"***Song Request for '{query}' has been received. Your song will be sent shortly.***\n"
            f"***Dev - @FUCXD***"
        )
        status = await update.message.reply_text(status_text, parse_mode='Markdown', reply_to_message_id=update.message.message_id)
        await process_download(update, query, status, update.message.message_id)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("dl_yes"):
        data_parts = query.data.split("|")
        link = data_parts[1]
        original_msg_id = int(data_parts[2])
        
        await query.edit_message_text("***Processing link... Please wait.***", parse_mode='Markdown')
        status = await query.message.reply_text(f"***Link detected! Sending shortly.\nDev - @FUCXD***", parse_mode='Markdown')
        await process_download(query, link, status, original_msg_id)
    elif query.data == "dl_no":
        await query.edit_message_text("***Ok, I will stay quiet 🤐 till next command***", parse_mode='Markdown')

# --- MAIN EXECUTION ---
async def main():
    app = Application.builder().token(TOKEN).build()
    
    await set_bot_commands(app)
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Console Output Only
    print(f"{GREEN}Bot running ----{RESET}")
    print(f"{BLUE}Dev -> {RED}@FUCXD{RESET}")

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    
    while True:
        await asyncio.sleep(10)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
