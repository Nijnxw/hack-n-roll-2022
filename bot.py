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
    elif data.startswith('d-'):
        get_drama_details(query)
    elif data.startswith('dr-'):
        get_drama_reviews(query)
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
        telebot.types.InlineKeyboardButton(drama["title"], callback_data="d-"+drama["title"])
        )
    bot.send_message(message.chat.id, 'Click the drama you would like to see info of:', reply_markup=keyboard)

def get_drama_selection(query):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Drama Info', callback_data='di-' + message.text[8:]),
        telebot.types.InlineKeyboardButton('Drama Reviews', callback_data='dr-' + message.text[8:])
        )
    bot.send_message(message.chat.id, 'Click the ?????:', reply_markup=keyboard)

def get_drama_details(query):
    send_drama_details(query.message, query.data[2:])

def send_drama_details(message, query):
    url = "https://kuryana.vercel.app/search/q/{"
    response = requests.get(url + query + "}")
    slug = response.json()["results"]["dramas"][0]["slug"]

    url = "https://kuryana.vercel.app/id/"
    response = requests.get(url + slug)
    drama = response.json()["data"]

    details = {
        "poster": drama.get("poster", ""),
        "link": drama.get("link", ""),
        "title": drama.get("title", ""),
        "score": drama.get("details", {}).get("score", ""),
        "country": drama.get("details", {}).get("country", ""),
        "episodes": drama.get("details", {}).get("episodes", ""),
        "aired": drama.get("details", {}).get("aired", ""),
        "duration": drama.get("details", {}).get("duration", ""),
        "content_rating": drama.get("details", {}).get("content_rating", ""),
        "tags": drama.get("others", {}).get("tags", ""),
        "genres": drama.get("others", {}).get("genres", ""),
        "synopsis": drama.get("synopsis", "")
    }

    message_text = f'''<a href='{details["poster"]}'>{'&#8203;'}</a>
<b><a href='{details['link']}'>{details["title"]}</a></b>
⭐️ Ratings: {details['score']}

<b>Title:</b><code> {details["title"]}</code>
<b>Country:</b><code> {details["country"]}</code>
<b>Episodes:</b><code> {details['episodes']}</code>
<b>Aired:</b><code> {details['aired']}</code>
<b>Duration:</b><code> {details['duration']}</code>
<b>Content Rating:</b><code> {details['content_rating']}</code>
<b>Genres:</b><code> {details['genres']}</code>
<b>Tags:</b><code> {details['tags']}</code>

<b>Synopsis:</b><code> {details['synopsis'][:500]}...</code>
    '''

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton('Drama Reviews', callback_data='dr-' + query))

    bot.send_message(
       message.chat.id, message_text,
       parse_mode='HTML',
       reply_markup=keyboard
   )

def get_drama_reviews(query):
    send_drama_details(query.message, query.data[3:])

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
