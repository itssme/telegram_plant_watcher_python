from telegram.ext import Updater, CommandHandler
import systemd.daemon
import datetime
import telegram
import logging
import sqlite3
import time
import cv2
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
chat_ids = []


def get_frame(vs):
    start_time = time.time()
    frame = None
    while time.time() - start_time <= 4 or frame is None:
        frame = vs.read()[1]

    return frame


def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Usage:\n"
                                                                    "/help - prints this help\n"
                                                                    "/register - saves your chat id for getting "
                                                                    "messages")


def add_chat_id(update, context):
    chat_id = update.message.chat_id
    db = sqlite3.connect("chats.db")
    cur = db.cursor()
    try:
        cur.execute("insert into chats values(?);", [chat_id])
        print(cur.fetchall())
    except Exception as e:
        print(e)
    cur.close()
    db.commit()
    db.close()
    print("inserted")
    update_ids()
    context.bot.send_message(chat_id=update.effective_chat.id, text="Saved your chat id")


def update_ids():
    global chat_ids
    db = sqlite3.connect("chats.db")
    cur = db.cursor()
    cur.execute("select * from chats;")
    chat_ids = [chat_id[0] for chat_id in cur.fetchall()]
    cur.close()
    print(chat_ids)
    print("[!] updated ids")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    global chat_ids

    db = None
    if not os.path.isfile("chats.db"):
        db = sqlite3.connect("chats.db")
        cur = db.cursor()
        cur.executescript("""create table chats (id varchar(256) primary key);""")
        cur.close()
    else:
        db = sqlite3.connect("chats.db")

    cur = db.cursor()
    cur.execute("select * from chats;")
    chat_ids = [chat_id[0] for chat_id in cur.fetchall()]
    cur.close()
    print(chat_ids)

    bot = telegram.Bot(token=os.environ["bot_token"])

    def send_all(text):
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text=text)

    def send_all_photo(filename):
        for chat_id in chat_ids:
            bot.send_photo(chat_id=chat_id, photo=open(filename, 'rb'))

    send_all("I am online again and stalking your plant (﻿ ͡° ͜ʖ ͡°)")

    updater = Updater(os.environ["bot_token"], use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("register", add_chat_id,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("help", help,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_error_handler(error)
    updater.start_polling()

    systemd.daemon.notify('READY=1')

    try:
        vs = cv2.VideoCapture(0)

        while True:
            current_time = datetime.datetime.now()
            next_date = datetime.datetime(current_time.year, current_time.month, current_time.day, hour=12, minute=0,
                                          second=0, microsecond=0)
            wait_time = next_date - current_time
            due = wait_time.seconds
            print("Waiting for " + str(due) + " seconds")

            if due < 0:
                send_all("There was an error in getting the next time")
                return

            time.sleep(due)
            frame = get_frame(vs)
            filename = os.environ["working_dir"] + "/" + str(datetime.datetime.now()).replace(".", "_").replace(" ",
                                                                                                          "_") + ".jpg"
            return_value = cv2.imwrite(filename, frame)
            send_all_photo(filename)

            if return_value:
                send_all("Image saved " + str(filename))
            else:
                send_all("Failed to save image :( " + str(filename))
            print(return_value)
            print("saved frame")

            # save a second image on the same day
            time.sleep(60*60)

            try:
                frame = get_frame(vs)
                filename = os.environ["working_dir"] + "/" + str(datetime.datetime.now()).replace(".", "_").\
                    replace(" ", "_") + ".jpg"

                return_value = cv2.imwrite(filename, frame)
                print(return_value)
                print("saved frame")
            except Exception as e:
                print(e)
                print("Unable to save second image :/")

    except Exception as e:
        send_all("Unknown error " + str(e))


if __name__ == '__main__':
    main()
