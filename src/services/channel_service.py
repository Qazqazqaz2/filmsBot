import os
from ..interfaces import IChannelManager

class TelegramChannelManager(IChannelManager):
    def __init__(self):
        self.channel_links = {
            "A1": os.getenv("CHANNEL_LINK_A1"),
            "A2": os.getenv("CHANNEL_LINK_A2"),
            "B1": os.getenv("CHANNEL_LINK_B1"),
            "B2": os.getenv("CHANNEL_LINK_B2"),
            "C1": os.getenv("CHANNEL_LINK_C1"),
            "C2": os.getenv("CHANNEL_LINK_C2")
        }
        
        self.channel_ids = {
            "A1": os.getenv("CHANNEL_ID_A1"),
            "A2": os.getenv("CHANNEL_ID_A2"),
            "B1": os.getenv("CHANNEL_ID_B1"),
            "B2": os.getenv("CHANNEL_ID_B2"),
            "C1": os.getenv("CHANNEL_ID_C1"),
            "C2": os.getenv("CHANNEL_ID_C2")
        }

    def get_channel_link(self, level: str) -> str:
        """Get channel link for specific level"""
        return self.channel_links.get(level, "")

    def get_channel_id(self, level: str) -> str:
        """Get channel ID for specific level"""
        return self.channel_ids.get(level, "")