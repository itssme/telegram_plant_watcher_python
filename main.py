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
vs = None


def snapshot(update, context):
    global vs

    if vs is not None:
        try:
            frame = get_frame(vs)
            filename = "/tmp/" + str(time.time()) + ".png"
            return_value = cv2.imwrite(filename, frame)
            logging.info("saving snapshop -> {}".format(return_value))
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(filename, 'rb'))
        except Exception as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text="There was an error: " + str(e))


def get_frame(vs):
    start_time = time.time()
    frame = None
    while time.time() - start_time <= 5:
        try:
            frame = vs.read()[1]
        except Exception as e:
            logging.error("could not capture image -> {}".format(e))
            time.sleep(1)

    logging.info("done getting frame")
    return frame


def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Usage:\n"
                                                                    "/help - prints this help\n"
                                                                    "/register - saves your chat id for getting "
                                                                    "messages\n"
                                                                    "/take_picture - takes a picture of the plant and "
                                                                    "sends it directly in telegram")


def add_chat_id(update, context):
    chat_id = update.message.chat_id
    db = sqlite3.connect("chats.db")
    try:
        cur = db.cursor()
        cur.execute("insert into chats values(?);", [chat_id])
        cur.close()
        db.commit()
        logging.info("inserted new chat id -> {}".format(chat_id))
    except Exception as e:
        logging.error("error while inserting new chat id -> {}".format(str(e)))
    finally:
        db.close()
    update_ids()
    context.bot.send_message(chat_id=update.effective_chat.id, text="Saved your chat id")


def update_ids():
    global chat_ids
    db = sqlite3.connect("chats.db")
    cur = db.cursor()
    cur.execute("select * from chats;")
    chat_ids = [chat_id[0] for chat_id in cur.fetchall()]
    cur.close()
    logging.info("updated ids -> {}".format(str(chat_ids)))


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    global chat_ids
    global vs

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
    logging.info("got chat ids from db -> {}".format(str(chat_ids)))

    bot = telegram.Bot(token=os.environ["bot_token"])

    def send_all(text):
        for chat_id in chat_ids:
            bot.send_message(chat_id=chat_id, text=text)

    def send_all_photo(filename):
        for chat_id in chat_ids:
            bot.send_photo(chat_id=chat_id, photo=open(filename, 'rb'))

    # send_all("I am online again and stalking your plant (﻿ ͡° ͜ʖ ͡°)")

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
    dp.add_handler(CommandHandler("take_picture", snapshot,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_error_handler(error)
    updater.start_polling()

    systemd.daemon.notify('READY=1')

    try:
        vs = cv2.VideoCapture(0)
        logging.info("opened video device")

        try:
            vs.set(cv2.CAP_PROP_FRAME_WIDTH, int(os.environ["width"]))
            vs.set(cv2.CAP_PROP_FRAME_HEIGHT, int(os.environ["height"]))
            logging.info("set resolution to width: {} and height: {}".format(os.environ["width"], os.environ["height"]))
        except Exception as e:
            logging.warning("could not change default resolution -> {}".format(str(e)))

        while True:
            current_time = datetime.datetime.now()
            next_date = datetime.datetime(current_time.year, current_time.month, current_time.day, hour=12, minute=0,
                                          second=0, microsecond=0)
            wait_time = next_date - current_time
            due = wait_time.seconds
            logging.info("Waiting for {} seconds".format(due))

            if due < 0:
                send_all("There was an error in getting the next time")
                return

            time.sleep(due)
            frame = get_frame(vs)

            if frame is None:
                logging.error("Failed to capture image")
                send_all("Failed to capture image, view log for details")
                time.sleep(60)
                continue

            filename = os.environ["working_dir"] + "/" + str(datetime.datetime.now()).replace(".", "_").replace(" ",
                                                                                                          "_") + ".jpg"
            return_value = cv2.imwrite(filename, frame)
            send_all_photo(filename)

            if return_value:
                send_all("Image saved " + str(filename))
            else:
                send_all("Failed to save image :( " + str(filename))
            logging.info("saved frame -> {}".format(return_value))

            # save a second image on the same day
            time.sleep(60*60)

            try:
                frame = get_frame(vs)
                filename = os.environ["working_dir"] + "/" + str(datetime.datetime.now()).replace(".", "_").\
                    replace(" ", "_") + ".jpg"

                return_value = cv2.imwrite(filename, frame)
                logging.info("saved frame -> {}".format(return_value))
            except Exception as e:
                logging.error("Unable to save second image -> {}".format(str(e)))

    except Exception as e:
        logging.info("Unknown error {}".format(str(e)))
        send_all("Unknown error " + str(e))


if __name__ == '__main__':
    main()
