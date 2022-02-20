import os
import telegram
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
load_dotenv(verbose=True)



updater = Updater(os.getenv("TOKEN"), use_context=True)
dispatcher = updater.dispatcher

if __name__ == "__main__":
    bot = telegram.Bot(os.getenv("TOKEN"))
    mc = os.getenv("chat_id")
    bot.send_message(mc, "안녕하세요")



'''custom_keyboard = [['top-left', 'top-right'], 
                   ['bottom-left', 'bottom-right']]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
bot.send_message(mc, 
                 text="Custom Keyboard Test", 
                 reply_markup=reply_markup)'''

def menu_choice(update, context):
    menu = [["1. 거래소 선택", "2. 주문설정"]
    , ["3. 주문설정", "4. 기타"]]
    reply_markup = telegram.ReplyKeyboardMarkup(menu)
    context.bot.send_message(chat_id=update.message.chat_id, text="작업을 선택해주세요", reply_markup=reply_markup)


menu_handler = CommandHandler("menu", menu_choice)
dispatcher.add_handler(menu_handler)

updater.start_polling()
updater.idle()
