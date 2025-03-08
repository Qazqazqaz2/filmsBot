import re
import requests
from bs4 import BeautifulSoup
from typing import List
from ..interfaces import ISubtitleFinder

class OpenSubtitlesService(ISubtitleFinder):
    def __init__(self):
        self.base_url = "https://www.opensubtitles.org"
        
    async def find_subtitles(self, movie_name: str) -> List[str]:
        """Find subtitles for a movie on OpenSubtitles"""
        try:
            movie_url = await self._get_movie_url(movie_name)
            if not movie_url:
                movie_url = await self._alternative_get_movie_url(movie_name)
                if not movie_url:
                    return []
                else:
                    return movie_url
            else:
                return await self._get_subtitle_links(movie_url)

        except Exception as e:
            print(f"Error finding subtitles: {e}")
            return []

    async def _get_movie_url(self, name: str) -> str:
        """Get movie page URL"""
        name = re.sub(r"[^\w\s]", "", name)
        search_name = name.lower().replace(" ", "+")
        
        try:
            req = requests.get(
                f"{self.base_url}/en/search2/moviename-{search_name}/sublanguageid-rus",
                verify=True
            )
        except Exception:
            req = requests.get(
                f"{self.base_url}/en/search2/moviename-{search_name}/sublanguageid-rus",
                verify=False
            )

        soup = BeautifulSoup(req.content, "lxml")
        blocks = soup.find_all("tr", class_="change even")
        
        if not blocks:
            return ""
            
        block = blocks[0].get("onclick")
        link = block.split("event,'")[-1].split("'")[0]
        return f"{self.base_url}{link}"

    async def _alternative_get_movie_url(self, name):
        name = re.sub(r"[^\w\s]", "", name)

        params = {
            'format': 'json3',
            'MovieName': name,
            'SubLanguageID': 'rus',
        }
        try:
            response = requests.get('https://www.opensubtitles.org/libs/suggest.php', params=params, verify=True)
        except Exception:
            response = requests.get('https://www.opensubtitles.org/libs/suggest.php', params=params, verify=False)

        link = "https://www.opensubtitles.org/en/search/sublanguageid-rus/idmovie-" + str(response.json()[0]["id"])
        try:
            response = requests.get(link, verify=True)
        except Exception:
            response = requests.get(link, verify=False)

        soup = BeautifulSoup(response.content, "lxml")
        blocks = soup.find_all("tr", class_="change")
        if not blocks:
            return []
        links = []
        for block in blocks:
            block = block.get("onclick").split(",'/")[-1].split("'")[0].split("/")[2]
            links.append(self.base_url+"/en/subtitleserve/sub/"+block)
        return links


    async def _get_subtitle_links(self, movie_url: str) -> List[str]:
        """Get subtitle download links"""
        try:
            req = requests.get(movie_url, verify=True)
        except Exception:
            req = requests.get(movie_url, verify=False)

        soup = BeautifulSoup(req.content, "lxml")
        links = []
        
        for td in soup.find_all("td", attrs={"align": "center"}):
            if td.find("span", attrs={"class": "p"}):
                try:
                    link = td.find("a").get("href")
                    links.append(f"{self.base_url}{link}")
                except Exception as e:
                    print(f"Error extracting link: {e}")
                    
        return links