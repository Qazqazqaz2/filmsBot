import os
import json
import requests
from typing import Optional, List
from ..interfaces import IMovieRecommender, IMovieDatabase

class GigaChatService(IMovieRecommender):
    def __init__(self, movie_db: IMovieDatabase):
        self.base_url = "https://gigachat.devices.sberbank.ru/api/v1"
        self.oauth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self._access_token = None
        self.movie_db = movie_db

    async def get_recommendation(self, level: str) -> str:
        """Get movie recommendation using GigaChat"""
        # Получаем список уже рекомендованных фильмов
        existing_movies = await self.movie_db.get_movies(level)
        
        access_token = await self._get_access_token()
        url = f"{self.base_url}/chat/completions"
        
        # Модифицируем промпт, чтобы исключить существующие фильмы
        existing_movies_str = ", ".join(existing_movies) if existing_movies else "нет"
        prompt = (
            f"подскажи название фильма на английском для изучения английского на уровне {level}. "
            f"Уже были рекомендованы следующие фильмы: {existing_movies_str}. "
            "Пожалуйста, порекомендуй фильм, которого нет в этом списке. "
            "В ответе должно быть только название фильма и ничего более"
        )
        
        payload = json.dumps({
            "model": "GigaChat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 1,
            "top_p": 0.1,
            "n": 1,
            "stream": False,
            "max_tokens": 512,
            "repetition_penalty": 1,
            "update_interval": 0
        })
        
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        return response.json()["choices"][0]["message"]["content"]

    async def _get_access_token(self) -> str:
        """Get access token for GigaChat API"""
        if self._access_token:
            return self._access_token

        payload = {
            'scope': 'GIGACHAT_API_PERS'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': os.getenv('GIGACHAT_RQUID'),
            'Authorization': os.getenv('GIGACHAT_AUTH')
        }
        
        response = requests.request("POST", self.oauth_url, headers=headers, data=payload, verify=False)
        self._access_token = response.json()["access_token"]
        return self._access_token