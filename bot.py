import os

# Python 3
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv
import telebot
import requests

config = load_dotenv(".env")
TOKEN = os.environ.get('TOKEN')

WEBHOOK_HOST = 'https://drama-and-anime-buddy.herokuapp.com/'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (TOKEN)

class WebhookHandler(BaseHTTPRequestHandler):
    server_version = "WebhookHandler/1.0"

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == WEBHOOK_URL_PATH and \
           'content-type' in self.headers and \
           'content-length' in self.headers and \
           self.headers['content-type'] == 'application/json':
            json_string = self.rfile.read(int(self.headers['content-length']))

            self.send_response(200)
            self.end_headers()

            update = telebot.types.Update.de_json(json_string)
            bot.process_new_messages([update.message])
        else:
            self.send_error(403)
            self.end_headers()

# PORT = int(os.environ.get('PORT', 5000))

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, '''
This is the list of commands that I know:

/start → Welcome message
/help → This message
/search [your input] → finds drama/anime/manga
    '''
    )

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
    elif data.startswith('recc-anime'):
        get_anime_recc(query)
    
    elif data.startswith('search-manga'):
        get_manga_callback(query)
    elif data.startswith('manga-'):
        get_manga_details(query)
    elif data.startswith('recc-manga'):
        get_manga_recc(query)
















###########################################
"""             DRAMA QUERY             """
###########################################

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
    send_drama_reviews(query.message, query.data[3:])

def send_drama_reviews(message, query):
    url = "https://kuryana.vercel.app/search/q/{"
    response = requests.get(url + query + "}")
    slug = response.json()["results"]["dramas"][0]["slug"]

    url = "https://kuryana.vercel.app/id/"
    response = requests.get(url + slug + "/reviews")
    data = response.json()["data"]
    reviews = response.json()["data"]["reviews"][:2]
    review_details = []
    for review in reviews:
        review_detail = {
            "reviewer_name": review.get("reviewer", {}).get("name", ""),
            "review": review.get("review", "A"*56)[0:len(review.get("review", ""))-56],
            "ratings-overall": review.get("ratings", {}).get("overall", ""),
            "ratings-story": review.get("ratings", {}).get("Story", ""),
            "ratings-acting": review.get("ratings", {}).get("Acting/Cast", ""),
            "ratings-music": review.get("ratings", {}).get("Music", ""),
            "ratings-rewatch": review.get("ratings", {}).get("Rewatch Value", ""),
            "info": review.get("reviewer", {}).get("info", ""),
        }
        review_details.append(review_detail)

    message_text = f'''
    <b><a href='{data.get("link", "")}'>{data.get("title", "")}</a></b>
    '''

    for i in range(0, 2):
        if i >= len(review_details):
            break
        review_detail = review_details[i]
        if i == 1:
            message_text += f'~' * 50
        message_text += f'''
<b>Reviewer Name:</b><code> {review_detail["reviewer_name"]}</code>
<b>Overall:</b><code> {review_detail["ratings-overall"]}/10</code>
<b>Story:</b><code> {review_detail["ratings-story"]}/10</code>
<b>Acting/Cast:</b><code> {review_detail["ratings-acting"]}/10</code>
<b>Music:</b><code> {review_detail["ratings-music"]}/10</code>
<b>Rewatch Value:</b><code> {review_detail["ratings-rewatch"]}/10</code>

<b>Review:</b><code> {review_detail['review'][:1500]}...</code>
<b>{review_detail["info"]}</b> 👍
    '''

    if len(review_details) == 0:
        message_text += f'''
        <b> There are no reviews at the moment </b>
        '''

    bot.send_message(
       message.chat.id, message_text,
       parse_mode='HTML',
       disable_web_page_preview=True
   )


















###########################################
"""             ANIME QUERY             """
###########################################

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
        keyboard.row(telebot.types.InlineKeyboardButton(title, callback_data="anime-" + str(anime["mal_id"])))
    
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

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton('🖥 Get other anime recommendations 🖥', callback_data="recc-anime" + query))

    title = details["title_english"] if details["title_english"] else details["title"]
    genres = ''
    for genre in details['genres']:
        genres += '#' + genre['name'] + ' '

    message_text = f'''
--------------------
|    <b>ANIME</b>     |
--------------------
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

    bot.send_message(message.chat.id, message_text, parse_mode='HTML', reply_markup=keyboard)

def get_anime_recc(query):
    bot.answer_callback_query(query.id)
    send_anime_recc(query.message, query.data[10:])

def send_anime_recc(message, query):
    url = f"https://api.jikan.moe/v4/anime/{query}/recommendations"
    response = requests.get(url)
    reccs = response.json()['data'][:5]

    if len(reccs) == 0:
        bot.send_message(message.chat.id, 'Sorry! There are no recommendations found 😔', parse_mode='HTML')
        return

    keyboard = telebot.types.InlineKeyboardMarkup()
    for recc in reccs:
        keyboard.row(telebot.types.InlineKeyboardButton(recc['entry']['title'], callback_data="anime-" + str(recc['entry']["mal_id"])))
    
    message_text = f'''
We have found <b><i>{len(reccs)}</i></b> animes!

Click on the manga to see more info:
    '''

    bot.send_message(message.chat.id, message_text, parse_mode='HTML', reply_markup=keyboard)




















###########################################
"""             MANGA QUERY             """
###########################################

def get_manga_callback(query):
    bot.answer_callback_query(query.id)
    send_manga_search_result(query.message, query.data[12:])

def send_manga_search_result(message, query):
    url = "https://api.jikan.moe/v4/manga?q="
    response = requests.get(url + query)
    mangas = response.json()['data']

    if len(mangas) == 0:
        bot.send_message(message.chat.id, 'Sorry! We couldn\'t find any manga 😔', parse_mode='HTML')
        return

    keyboard = telebot.types.InlineKeyboardMarkup()
    for manga in mangas:
        title = manga["title_english"] if manga["title_english"] else manga["title"]
        keyboard.row(telebot.types.InlineKeyboardButton(title, callback_data="manga-" + str(manga["mal_id"])))
    
    message_text = f'''
We have found <b><i>{len(mangas)}</i></b> mangas!

Click on the manga to see more info:
    '''

    bot.send_message(message.chat.id, message_text, parse_mode='HTML', reply_markup=keyboard)

def get_manga_details(query):
    bot.answer_callback_query(query.id)
    send_manga_details(query.message, query.data[6:])

def send_manga_details(message, query):
    url = "https://api.jikan.moe/v4/manga/"
    response = requests.get(url + query)
    details = response.json()['data']

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton('📚 Get other manga recommendations 📚', callback_data="recc-manga" + query))

    title = details["title_english"] if details["title_english"] else details["title"]
    genres = ''
    for genre in details['genres']:
        genres += '#' + genre['name'] + ' '

    message_text = f'''
--------------------
|   <b>MANGA</b>    |
--------------------
<b><a href='{details['url']}'>{title}</a> ({details['published']['prop']['from']['year']})</b>
⭐️ Ratings: {details['scored']} / 10 from {details['scored_by']} users

<code>{details['synopsis'][:200]}...</code>

<b>Title:</b><code> {title}</code>
<b>Chapters:</b><code> {details['chapters']}</code>
<b>Volumes:</b><code> {details['volumes']}</code>
<b>Status:</b><code> {details['status']}</code>
<b>Published:</b><code> {details['published']['string']}</code>

Genre: {genres}
    '''

    bot.send_message(message.chat.id, message_text, parse_mode='HTML', reply_markup=keyboard)

def get_manga_recc(query):
    bot.answer_callback_query(query.id)
    send_manga_recc(query.message, query.data[10:])

def send_manga_recc(message, query):
    url = f"https://api.jikan.moe/v4/manga/{query}/recommendations"
    response = requests.get(url)
    reccs = response.json()['data'][:5]

    if len(reccs) == 0:
        bot.send_message(message.chat.id, 'Sorry! There are no recommendations found 😔', parse_mode='HTML')
        return

    keyboard = telebot.types.InlineKeyboardMarkup()
    for recc in reccs:
        keyboard.row(telebot.types.InlineKeyboardButton(recc['entry']['title'], callback_data="manga-" + str(recc['entry']["mal_id"])))
    
    message_text = f'''
We have found <b><i>{len(reccs)}</i></b> mangas!

Click on the manga to see more info:
    '''

    bot.send_message(message.chat.id, message_text, parse_mode='HTML', reply_markup=keyboard)








### Allow bot to listen for messages
# bot.infinity_polling()

# bot.start_webhook(listen="0.0.0.0",
#                           port=int(PORT),
#                           url_path=TOKEN)
# bot.set_webhook('https://drama-and-anime-buddy.herokuapp.com/' + TOKEN)

# Start server
httpd = HTTPServer((WEBHOOK_LISTEN, WEBHOOK_PORT),
                   WebhookHandler)

# httpd.socket = ssl.wrap_socket(httpd.socket,
#                                certfile=WEBHOOK_SSL_CERT,
#                                keyfile=WEBHOOK_SSL_PRIV,
#                                server_side=True)

httpd.serve_forever()
