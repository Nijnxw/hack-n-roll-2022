import os
import logging

from dotenv import load_dotenv
import telebot
import requests

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

config = load_dotenv(".env")
TOKEN = os.environ.get('TOKEN')

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['search'])
def exchange_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Drama', callback_data='search-drama' + message.text[8:]),
        telebot.types.InlineKeyboardButton('Anime', callback_data='search-anime' + message.text[8:]),
        telebot.types.InlineKeyboardButton('Manga', callback_data='search-manga' + message.text[8:])
        )
    bot.send_message(message.chat.id, 'Click the ?????:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(query):
    data = query.data
    if data.startswith('search-drama'):
        get_drama_callback(query)
    elif data.startswith('drama-'):
        get_drama_details(query)
    elif data.startswith('search-anime'):
        get_anime_callback(query)
    elif data.startswith('anime-'):
        get_anime_details(query)

""" DRAMA QUERY """

def get_drama_callback(query):
    bot.answer_callback_query(query.id)
    send_drama_search_result(query.message, query.data[12:])

def send_drama_search_result(message, query):
    url = "https://kuryana.vercel.app/search/q/{"
    response = requests.get(url + query + "}")
    dramas = response.json()["results"]["dramas"]

    keyboard = telebot.types.InlineKeyboardMarkup()
    for drama in dramas:
        keyboard.row(
        telebot.types.InlineKeyboardButton(drama["title"], callback_data="drama-" + drama["slug"])
        )
    bot.send_message(message.chat.id, 'Click the drama you would like to see info of:', reply_markup=keyboard)

def get_drama_details(query):
    bot.answer_callback_query(query.id)
    send_drama_details(query.message, query.data[6:])

def send_drama_details(message, query):
    # Working on it
    return

""" ANIME QUERY """

def get_anime_callback(query):
    bot.answer_callback_query(query.id)
    send_anime_search_result(query.message, query.data[12:])

def send_anime_search_result(message, query):
    url = "https://api.jikan.moe/v4/anime?q="
    response = requests.get(url + query)
    animes = response.json()['data']

    if len(animes) == 0:
        bot.send_message(message.chat.id, 'Sorry! We couldn\'t find any animes 😔', parse_mode='HTML')
        return

    keyboard = telebot.types.InlineKeyboardMarkup()
    for anime in animes:
        title = anime["title_english"] if anime["title_english"] else anime["title"]
        print
        keyboard.row(
        telebot.types.InlineKeyboardButton(title, callback_data="anime-" + str(anime["mal_id"]))
        )
    
    message_text = f'''
We have found <b><i>{len(animes)}</i></b> animes!

Click on the anime to see more info:
    '''

    bot.send_message(message.chat.id, message_text, parse_mode='HTML', reply_markup=keyboard)

def get_anime_details(query):
    bot.answer_callback_query(query.id)
    send_anime_details(query.message, query.data[6:])

def send_anime_details(message, query):
    url = "https://api.jikan.moe/v4/anime/"
    response = requests.get(url + query)
    details = response.json()['data']
    print('\n\n', details.keys())

    title = details["title_english"] if details["title_english"] else details["title"]
    genres = ''
    for genre in details['genres']:
        genres += '#' + genre['name'] + ' '

    message_text = f'''
<b><a href='{details['url']}'>{title}</a> ({details['year']})</b>
⭐️ Ratings: {details['score']} / 10 from {details['scored_by']} users

<code>{details['synopsis'][:200]}...</code>

<b>Title:</b><code> {title}</code>
<b>Episodes:</b><code> {details['episodes']}</code>
<b>Status:</b><code> {details['status']}</code>
<b>Aired:</b><code> {details['aired']['string']}</code>
<b>Duration:</b><code> {details['duration']}</code>

Genre: {genres}
    '''

    bot.send_message(message.chat.id, message_text, parse_mode='HTML')

bot.infinity_polling()

# # Enable logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
# )

# logger = logging.getLogger(__name__)

 
# # Define a few command handlers. These usually take the two arguments update and
# # context.
# def start(update: Update, context: CallbackContext) -> None:
#     """Send a message when the command /start is issued."""
#     user = update.effective_user
#     update.message.reply_markdown_v2(fr'Hi {user.mention_markdown_v2()}\!')


# def help_command(update: Update, context: CallbackContext) -> None:
#     """Send a message when the command /help is issued."""
#     update.message.reply_text('Help!')


# def echo(update: Update, context: CallbackContext) -> None:
#     """Echo the user message."""
#     update.message.reply_text(update.message.text)

# def error(update, context):
#     """Log Errors caused by Updates."""
#     logger.warning('Update "%s" caused error "%s"', update, context.error)

# def main() -> None:
#     """Start the bot."""
#     # Create the Updater and pass it your bot's token.
#     updater = Updater(token=TOKEN, use_context=True)

#     # Get the dispatcher to register handlers
#     dispatcher = updater.dispatcher

#     # on different commands - answer in Telegram
#     dispatcher.add_handler(CommandHandler("start", start))
#     dispatcher.add_handler(CommandHandler("help", help_command))

#     # on non command i.e message - echo the message on Telegram
#     dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

#     # log all errors
#     dispatcher.add_error_handler(error)

#     # Start the Bot
#     updater.start_polling()

#     # Run the bot until you press Ctrl-C or the process receives SIGINT,
#     # SIGTERM or SIGABRT. This should be used most of the time, since
#     # start_polling() is non-blocking and will stop the bot gracefully.
#     updater.idle()


# if __name__ == '__main__':
#     main()