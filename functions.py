from variables import HOME_API, ENV_PATH, SEARCH_API, FETCH_TV_SERIES, DOWNLOAD_API
from browser import Browser, Response
from requests.utils import requote_uri

from logging_module import logger

smily_emoji = "\U0001f642"
shushing_emoji = "\U0001F92B"


def handle_response(text: str, username: str) -> str:
    if 'hi' in text or 'hello' in text:
        return f'Hello {username}, nice to meet you!'
    
    if 'how are you' in text:
        return 'I\'m good, thanks'
    
    if 'bby' in text or 'ashish' in text:
        return 'Ashish is working on me, I\'m getting better at this ' + smily_emoji
    
    if 'bye' in text:
        return 'Bye! Have a nice day..'
    
    if 'love you' in text:
        return 'Aww, thanks'
    
    if 'who created you' in text:
        return 'I was created by Ashish Kandu'
    
    if 'what do you do' in text or 'what is your purpose' in text or 'purpose' in text:
        return 'I was created to help my developer get the links from his script to watch series'
    
    if text == 'ok' or text == 'okay':
        return smily_emoji
    
    if '?' == text:
        return 'hmmm..'

    if 'what is he doing' in text:
        return 'Ashish is missing you' + shushing_emoji
    
    if 'call' in text:
        return 'I\'ll try to let him know on this'
    
    if 'do you love me' in text:
        return 'Sorry, I\'m too busy for your romance'
    
    return 'I don\'t understand that, could you please rephrase it?'


def get_token_links(tokenless_links: list, session: Browser) -> list:
    return [link+session.headers['Authorization'].replace('Bearer ', '') for link in tokenless_links]


def is_valid_token(session: Browser) -> Response:
    return session.get(HOME_API) # Check the status of cached token


def update_token(session: Browser) -> bool:
    response = session.get_new_token()
    if response.ok:
        return True
    logger.info(response.json())
    return False

    
def search_in_plex(session: Browser, keyword: str) -> Response:
    prepared_url: str = f'{SEARCH_API}/{requote_uri(keyword)}'
    return session.get(prepared_url)


def fetch_series(session: Browser, tv_id: str) -> Response:
    prepared_url: str = f'{FETCH_TV_SERIES}/{tv_id}'
    return session.get(prepared_url)


def extract_links_from_response(response_obj: Response, quality: str) -> dict:
    seasons = response_obj.json()['seasons'][quality.rstrip('p')]
    data = {} # store data extracted from response json
    for season in seasons:
        episodes = seasons[season]["episodes"] #List of episodes[dict] in current season
        data[season] = [f'{DOWNLOAD_API}/{episode["name"]}?id={episode["_id"]}&token=' for episode in episodes]
    return data