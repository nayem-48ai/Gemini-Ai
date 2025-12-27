import os
import telebot
import google.generativeai as genai
from flask import Flask
from threading import Thread
import datetime
import requests
from PIL import Image
from io import BytesIO

# আপনার API Key এবং Token এখানে বসান
API_KEY = "AIzaSyA4bP8Hrzvp_OuYSZxlV8gceL3cgmrNQRc"
BOT_TOKEN = "8452171958:AAFElgfh2yXz7VurqsOBZD3AJIpvTCB8GmE"

# Gemini কনফিগারেশন
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # দ্রুত রেসপন্সের জন্য ফ্ল্যাশ ব্যবহার করা হয়েছে

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

# /start কমান্ড
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "হ্যালো! আমি আপনার AI অ্যাসিস্ট্যান্ট।\n\n১. যেকোনো প্রশ্ন করতে পারেন।\n২. ছবি দিয়ে তার বর্ণনা বা এডিট করতে বলতে পারেন।\n৩. সময় জানতে 'সময় কত' লিখুন।")

# টেক্সট মেসেজ হ্যান্ডলার
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    text = message.text.lower()

    if "নাম কি" in text:
        bot.reply_to(message, "আমার নাম Nano Gemini Bot।")
    elif "সময়" in text or "বাজে" in text:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        bot.reply_to(message, f"এখন সময়: {now}")
    else:
        # Gemini দিয়ে উত্তর জেনারেট করা
        try:
            response = model.generate_content(message.text)
            bot.reply_to(message, response.text)
        except Exception as e:
            bot.reply_to(message, "দুঃখিত, আমি এখন উত্তর দিতে পারছি না।")

# ইমেজ মেসেজ হ্যান্ডলার (Photo + Prompt)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    prompt = message.caption if message.caption else "Describe this image"
    
    bot.reply_to(message, "ছবিটি প্রসেস করছি, দয়া করে অপেক্ষা করুন...")

    try:
        # ছবি ডাউনলোড করা
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        img = Image.open(BytesIO(downloaded_file))
        
        # Gemini Vision ব্যবহার করে ছবি ও প্রম্পট বিশ্লেষণ
        response = model.generate_content([prompt, img])
        bot.reply_to(message, response.text)
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

# বট চালু রাখা
def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    print("Bot is alive!")
    bot.infinity_polling()
