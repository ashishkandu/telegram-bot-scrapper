from telegram import (
    Update, 
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import ContextTypes

from functions import handle_response, get_token_links, is_valid_token, update_token, search_in_plex, fetch_series, extract_links_from_response
from requests.utils import requote_uri
from logging_module import logger
import json

from browser import Browser

# Creating Browser object and a response object
my_browser = Browser()


async def inline_link_provider(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query
    if not query:
        return
    elif not query.isnumeric():
        await context.bot.answer_inline_query(update.inline_query.id, [InlineQueryResultArticle(id=query, title='Try only season no. without any string', input_message_content=InputTextMessageContent('/info'))])
        return
    elif not my_browser.cached_data:
        await context.bot.answer_inline_query(update.inline_query.id, [InlineQueryResultArticle(id=query, title='Search for a series first', input_message_content=InputTextMessageContent('/info'))])
        return
    results = []
    try:
        links = get_token_links(my_browser.cached_data[query], my_browser)
    except KeyError:
        await context.bot.answer_inline_query(update.inline_query.id, [InlineQueryResultArticle(id=query, title=f'{my_browser.info_data["name"]} does not have season {query}', input_message_content=InputTextMessageContent('/info'))])
        return
    for index, episode in enumerate(links, start=1):
        episode_title = episode.split('?')[0].split('/')[-1]
        if 'the big bang theory' in episode_title.lower():
            episode_title = 'TBBT ' + episode_title[20:]
        results.append(
            InlineQueryResultArticle(
                id=index,
                title=episode_title,
                input_message_content=InputTextMessageContent(f'<a href="{requote_uri(episode)}">{episode_title}</a>', parse_mode='HTML')
            )
    )
    await context.bot.answer_inline_query(update.inline_query.id, results)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="Hi, I'm Sumu! Ready to serve series links for you")

# This function utilizes pre definded responses and talk to the user
async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = str(update.message.text).lower()
    user_name = update.message.from_user.first_name
    response = ''

    logger.info(f'User ({update.message.chat_id}) says "{text}" in {message_type}')

    if message_type == 'group':
        if '@mysumu_bot' in text:
            new_text = text.replace('@mysumu_bot', '').strip()
            response = handle_response(new_text, user_name)
    else:
        response = handle_response(text, user_name)

    await update.message.reply_text(text=response)


# Test function is to caps the message passed as /caps ashish
async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text_caps = ' '.join(context.args).upper()
    await update.message.reply_text(text=text_caps)


async def get_all_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """This function fetches all the links available in the cached data for a particular season # """
    if not my_browser.cached_data: # Checks if cached data is empty
        await update.message.reply_text(text="No cached data, search for a series")
        return
    message = str(update.message.text).strip('/season').strip()
    try:
        season_no, starting_episode = message.split()
    except ValueError:
        season_no = message
        starting_episode = 0
    if not season_no.isnumeric():
        logger.info(f'{update.message.from_user.first_name} searched for season {season_no}')
        await update.message.reply_text(text=f'The {my_browser.info_data["name"]} does not have season {season_no}')
        return
    try:
        links = get_token_links(my_browser.cached_data[season_no], my_browser)
    except KeyError:
        await update.message.reply_text(text=f'{my_browser.info_data["name"]} does not have season {season_no}')
        return
    for episode in links[int(starting_episode):]:
        episode_title = episode.split('?')[0].split('/')[-1]
        await update.message.reply_text(text=f'<a href="{requote_uri(episode)}">{episode_title}</a>', parse_mode='HTML')


async def get_token_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Validates the token cached in the env"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Verifying...")
    response = is_valid_token(my_browser)
    
    # The options will be presented to the user
    reply_keyboard = [["/renew", "/cancel"]]

    if not response.ok:
        logger.info(response.text)
        response_text = response.json()['message'] + ' \U0001F494'
    else:
        logger.info(response)
        response_text = 'Token is healthy \U0001F49A'

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)
    await update.message.reply_text("Do you want to renew the token?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))  


async def renew(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Renews the token stored in the env file"""
    # if my_browser.get_new_token():
    if update_token(my_browser):
        update_text="Token renewal complete!"
    else:
        update_text="Authentication failed"
    await update.message.reply_text(text=update_text, reply_markup=ReplyKeyboardRemove())


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(text='Operation canceled', reply_markup=ReplyKeyboardRemove())


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    search_keyword = ' '.join(context.args)
    logger.info(f'{update.message.from_user.first_name} searched for {search_keyword}')
    response = search_in_plex(my_browser, search_keyword)
    if not response.ok:
        response_message = "Enter a keyword to search e.g,\n/search The big bang theory"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)
        return
    if not response.json():
        response_message = "Not Found"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)
        return
    search_results = []
    for search_item in response.json():
        search_results.append([InlineKeyboardButton(search_item['title'], callback_data=search_item['id'])])
    reply_markup = InlineKeyboardMarkup(search_results)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


async def search_result_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    # selected = query.data
    response = fetch_series(my_browser, query.data)
    with open('temp.json', 'w') as f:
        json.dump(response.json(), f, indent=2)
    if response.ok:
        if not my_browser.store_current_response(response):
            await query.edit_message_text('unable to save info')
            return
        quality_available = []
        for quality in response.json()['quality']:
            quality_available.append([InlineKeyboardButton(quality+'p', callback_data=quality+'p')])
        reply_markup = InlineKeyboardMarkup(quality_available)
        await query.edit_message_text(text=f"{response.json()['name']}\n{response.json()['overview']}\n\nChoose quality: ", reply_markup=reply_markup)
        # await context.bot.sendMessage(chat_id=update.effective_chat.id, text= 'hello', reply_markup=keyboard)
    else:
        await query.edit_message_text('Series not found')

    
async def extract_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if my_browser.get_current_response().status_code == None:
        return
    data = extract_links_from_response(my_browser.get_current_response() , query.data)
    if my_browser.store_data(data):
        await query.edit_message_text(f"{my_browser.get_current_response().json()['name']} saved successfully!")
    else:
        await query.edit_message_text("Something went wrong while saving the data")
        
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    info_data = my_browser.info_data
    if not info_data:
        await update.message.reply_text(text="No information found")
        return
    message = f"{info_data['name']} - {(', '.join([data+'p' for data in info_data['quality']]))}\n\n{info_data['overview']}\n\nFirst air date: {info_data['first_air_date']}"
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=info_data['poster_path'], caption=message)
