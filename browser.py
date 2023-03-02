from dotenv import get_key, set_key
from requests import Session, Response
from variables import LOGIN_API, DATA_FILE_NAME, INFO_FILE_NAME, ENV_PATH
import json


class Browser(Session):

    def __init__(self):
       super().__init__()
       self.headers = {
            'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://googolplex.live/',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Linux"',
        }
       self.inject_header({'Authorization': 'Bearer ' + get_key(ENV_PATH, 'PLEX_TOKEN')})

       try:
        with open(DATA_FILE_NAME) as f:
            self.cached_data = json.load(f)
       except FileNotFoundError:
           self.cached_data = {}
        
       try:
        with open(INFO_FILE_NAME) as f:
            self.info_data = json.load(f)
       except FileNotFoundError:
           self.info_data = {}
       except json.decoder.JSONDecodeError:
           self.info_data = {}

       
    def login(self, username: str, password: str) -> Response:
        payload = {
            'email': username,
            'password': password
        }
        return self.post(LOGIN_API, json=payload)
    
    def get_new_token(self) -> Response:
        self.remove_header('Authorization')
        username = get_key(ENV_PATH, 'USER_NAME')
        password = get_key(ENV_PATH, 'PASSWORD')
        response: Response = self.login(username, password)
        if response.ok:
            plex_token = response.json()['token']
            set_key(ENV_PATH, 'PLEX_TOKEN', plex_token)
            self.inject_header({'Authorization': 'Bearer ' + plex_token})
            print(plex_token)
        return response
    
    
    def inject_header(self, data: dict) -> None:
        self.headers.update(data)

    def remove_header(self, key: str):
        self.headers.pop(key, None)

    def store_current_response(self, response: Response) -> None:
        self.response = response
        try:
            informations = {
                    'name': response.json()['name'],
                    'overview': response.json()['overview'],
                    'first_air_date': response.json()['first_air_date'],
                    'quality': response.json()['quality'],
                    'poster_path': response.json()['poster_path'],
                    }
            with open(INFO_FILE_NAME, 'w', encoding='utf-8') as f:
                json.dump(
                    informations,
                    f, 
                    indent=2
                )
            self.info_data = informations # Gets the latest information
            return True
        except:
            return False
    
    def get_current_response(self) -> Response:
        return self.response
    
    def store_data(self, data: dict) -> bool:
        self.cached_data = data
        try:
            with open(DATA_FILE_NAME, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except:
            return False

    def get_cached_data(self) -> dict:
        return self.cached_data