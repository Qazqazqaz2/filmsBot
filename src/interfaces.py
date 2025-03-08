from abc import ABC, abstractmethod
from typing import List

class IMovieRecommender(ABC):
    @abstractmethod
    async def get_recommendation(self, level: str) -> str:
        """Get movie recommendation for specific English level"""
        pass

class ISubtitleFinder(ABC):
    @abstractmethod
    async def find_subtitles(self, movie_name: str) -> List[str]:
        """Find subtitles for a movie"""
        pass

class IChannelManager(ABC):
    @abstractmethod
    def get_channel_link(self, level: str) -> str:
        """Get channel link for specific level"""
        pass

    @abstractmethod
    def get_channel_id(self, level: str) -> str:
        """Get channel ID for specific level"""
        pass

class IMovieDatabase(ABC):
    @abstractmethod
    async def init_db(self) -> None:
        """Initialize database and create tables if not exist"""
        pass

    @abstractmethod
    async def save_movie(self, level: str, movie_name: str) -> None:
        """Save movie to specific level table"""
        pass

    @abstractmethod
    async def get_movies(self, level: str) -> List[str]:
        """Get all movies for specific level"""
        pass