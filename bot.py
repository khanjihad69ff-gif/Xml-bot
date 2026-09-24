import telebot
from telebot import types
import json
import os
import random
from flask import Flask, request

TOKEN = "8810688330:AAEHpDUUQz5kpsb-_9m-kctq9nDmMqICLDc"
CHANNEL_USERNAME = "@Zihad_Editz"
ADMIN_ID = 8017043698  # আপনার অ্যাডমিন আইডি

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "files_db.json"

# ফ্লাস্ক সার্ভার (ক্লাউডে বট সচল রাখার জন্য জরুরি)
server = Flask(__name__)

def load_db():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# মেম্বারশিপ চেক করার ফাংশন
def is_user_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print(f"Error: {e}")
    return False

# অ্যাডমিন ফাইল আপলোড করলে লিংক জেনারেট হবে
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "You are not authorized to upload files here!")
        return
        
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_code = f"xml_{random.randint(1000, 9999)}"
    
    db = load_db()
    db[file_code] = {
        "file_id": file_id,
        "file_name": file_name
    }
    save_db(db)
    
    bot_info = bot.get_me()
    share_link = f"https://t.me/{bot_info.username}?start={file_code}"
    
    bot.reply_to(
        message,
        f"<b>✨ ফাইল সফলভাবে সেভ হয়েছে!</b>\n\n"
        f"📁 <b>নাম:</b> {file_name}\n"
        f"🔗 <b>শেয়ার লিংক:</b>\n<code>{share_link}</code>",
        parse_mode="HTML"
    )

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    text = message.text
    
    args = text.split()
    file_code = args[1] if len(args) > 1 else None
    
    if not is_user_member(user_id):
        markup = types.InlineKeyboardMarkup()
        btn_join = types.InlineKeyboardButton("📢 চ্যানেলে জয়েন করুন", url="https://t.me/Zihad_Editz")
        
        callback_data = f"verify_{file_code}" if file_code else "verify_normal"
        btn_verify = types.InlineKeyboardButton("✅ Verify", callback_data=callback_data)
        
        markup.add(btn_join)
        markup.add(btn_verify)
        
        guide_text = (
            "<b>🔐 ফাইল পাওয়ার নিয়ম:</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "<b>①</b> নিচের চ্যানেল Join করুন।\n"
            "<b>②</b> জয়েন সম্পন্ন হলে Verify বাটনে চাপুন।\n"
            "<b>③</b> Verification সফল হলে ফাইল সরাসরি পেয়ে যাবেন।"
        )
        
        bot.send_message(
            message.chat.id,
            guide_text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        return

    if file_code:
        send_file_by_code(message.chat.id, file_code)
    else:
        welcome_text = (
            "<b>👋 স্বাগতম! Zihad XML Bot-এ আপনাকে স্বাগতম। ✨</b>\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "📁 এই বটটির মাধ্যমে আপনি খুব সহজেই প্রয়োজনীয় এবং প্রিমিয়াম সকল **XML File** সংগ্রহ করতে পারবেন।\n\n"
            "🔥 <b>আমাদের বিশেষ সুবিধাসমূহ:</b>\n"
            "❌ কোনো বিরক্তিকর শর্টনার বা লিংক জাম্পিংয়ের ঝামেলা নেই!\n"
            "🚫 কোনো অতিরিক্ত বিজ্ঞাপন (Ad) ছাড়াই ফাইল পাবেন।\n"
            "⚡ শুধু একবার চ্যানেলে জয়েন করে খুব দ্রুত ও নিরাপদে ফাইল সংগ্রহ করুন।\n\n"
            "🚀 <i>যেকোনো ফাইলের লিংকে ক্লিক করে বটে প্রবেশ করুন এবং সহজে ফাইল নিন!</i>"
        )
        bot.send_message(message.chat.id, welcome_text, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    
    if data.startswith("verify_"):
        file_code = data.split("_", 1)[1] if "_" in data else None
        
        if is_user_member(user_id):
            bot.answer_callback_query(call.id, "সফলভাবে ভেরিফিকেশন সম্পন্ন হয়েছে! 🎉")
            
            if file_code and file_code != "normal":
                send_file_by_code(call.message.chat.id, file_code)
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except:
                    pass
            else:
                bot.edit_message_text(
                    "<b>ভেরিফিকেশন সফল হয়েছে! ✅</b>\n\nএখন আপনার লিংকে আবার ক্লিক করুন অথবা /start কমান্ড দিন।",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    parse_mode="HTML"
                )
        else:
            bot.answer_callback_query(call.id, "আপনি এখনো চ্যানেলে জয়েন করেননি! আগে চ্যানেলে জয়েন করুন। ❌", show_alert=True)

def send_file_by_code(chat_id, file_code):
    db = load_db()
    if file_code in db:
        file_data = db[file_code]
        bot.send_document(
            chat_id,
            file_data["file_id"],
            caption=f"<b>🎉 আপনার কাঙ্ক্ষিত ফাইলটি নিচে দেওয়া হলো:</b>\n📁 {file_data['file_name']}",
            parse_mode="HTML"
        )
    else:
        bot.send_message(chat_id, "দুঃখিত, ফাইলটি পাওয়া যায়নি অথবা লিংকটির মেয়াদ শেষ হয়ে গেছে! ❌")

# ফ্লাস্ক ওয়েব হুক রুট (ক্লাউড সার্ভারের জন্য)
@server.route('/')
def webhook():
    return "Bot is running 24/7!", 200

if __name__ == "__main__":
    # ব্যাকগ্রাউন্ডে টেলিগ্রাম বট পোলিং চালু করা
    import threading
    bot_thread = threading.Thread(target=bot.infinity_polling)
    bot_thread.start()
    
    # ফ্লাস্ক সার্ভার রান করা (পোট বাইন্ডিং)
    port = int(os.environ.get("PORT", 5000))
    server.run(host="0.0.0.0", port=port)
    
