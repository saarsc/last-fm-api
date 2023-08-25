from requests import session, Session
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from time import sleep
from typing import Union
from utils import url_decode, flatten_list, is_cached, read_from_cache, write_to_cache

class LastFMApi():
  def __init__(self, use_chace=True, cache_folder="pages", delay=2, username="", password="", date=None) -> None:
    self.use_cache: bool = use_chace
    self.cache_folder: str = cache_folder
    self.delay: float = delay
    self.username: str = username
    self.date: str = date
    self.auth(username, password)

  @property
  def url(self):
    url = f"https://www.last.fm/user/{self.username}/library"
    if self.date:
      url += f"?from={self.date}"
    
    return url
  
  @classmethod
  def auth(self, username, password) -> session:
    _s: Session = session()
    login_page = BeautifulSoup(
      _s.get("https://www.last.fm/login").content
    )

    csrf = login_page.find("input", {
      "name": "csrfmiddlewaretoken"
    })["value"]

    payload = {
      "csrfmiddlewaretoken":csrf,
      "next": "/user/_",
      "username_or_email": username,
      "password": password,
      "submit": ""
    }

    headers = {
      "Cache-Control": "max-age=0", 
      "Sec-Ch-Ua": "\"Chromium\";v=\"107\", \"Not=A?Brand\";v=\"24\"", 
      "Sec-Ch-Ua-Mobile": "?0", 
      "Sec-Ch-Ua-Platform": "\"Windows\"", 
      "Upgrade-Insecure-Requests": "1", 
      "Origin": "https://www.last.fm", 
      "Content-Type": "application/x-www-form-urlencoded",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.107 Safari/537.36", 
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
      "Sec-Fetch-Site": "same-origin", 
      "Sec-Fetch-Mode": "navigate", 
      "Sec-Fetch-User": "?1", 
      "Sec-Fetch-Dest": "document", 
      "Referer": "https://www.last.fm/login", 
      "Accept-Encoding": "gzip, deflate", 
      "Accept-Language": 
      "en-US,en;q=0.9"
    }

    r = _s.post("https://www.last.fm/login", data=payload, headers=headers)
    setattr(self, "session", _s)
    return _s

  def page_url(self, page_num: int) -> str:
    char = "?"
    if self.date:
      char = "&"
    
    return f"{self.url}{char}page={page_num}"

  def get_page(self, page_num: int) -> str:
    if self.use_cache:
      if is_cached(page_num, self.cache_folder):
        return read_from_cache(f"{page_num}.html", self.cache_folder)

    page = self.session.get(self.page_url(page_num)).content.decode()
    if self.use_cache:
      write_to_cache(f"{page_num}.html", self.cache_folder, page)

    return page

  def get_single_list_page_soup(self, page_num: int) -> BeautifulSoup:
    return BeautifulSoup(
      self.get_page(page_num),
      "html.parser"
    )

  def get_property_by_class(self, soup: BeautifulSoup, class_name: str) -> list[Tag]:
    return soup.find_all(class_=class_name)

  def get_class_text(self, soup: BeautifulSoup, class_name: str) -> list[str]:
    return list(
      map(
        lambda artist: artist.text.strip(), self.get_property_by_class(soup, class_name)
      )
    )

  def get_artists(self, soup: BeautifulSoup) -> list[str]:
    return self.get_class_text(soup, "chartlist-artist")

  def get_names(self, soup: BeautifulSoup) -> list[str]:
    return self.get_class_text(soup, "chartlist-name")
  
  def extract_album_name(self, album: Tag) -> str:
    album_link = album.find("a")
    if album_link:
      album_link = album_link["href"]
      return url_decode(album_link[album_link.rindex("/")+1:])

    return ""

  def get_albums(self, soup: BeautifulSoup) -> list[str]:
    return list(
      map(
        self.extract_album_name,
        self.get_property_by_class(soup, "chartlist-image")
      )
    )

  def get_timestamps(self, soup: BeautifulSoup) -> list[datetime]:
    return list(
      map(
        lambda song: datetime.strptime(
          song.find("span")["title"], "%A %d %b %Y, %I:%M%p"
        ),
        self.get_property_by_class(soup, "chartlist-timestamp")
      )
    )

  def get_pages_count(self) -> int:
    return int(
      self.get_single_list_page_soup(1).find_all(
        class_="pagination-page")[-1].text.strip()
    )

  def get_page_data(self, soup: BeautifulSoup) -> Union[list[str], list[str], list[datetime], list[str]]:
    return self.get_names(soup), self.get_artists(soup), self.get_timestamps(soup), self.get_albums(soup)

  def merge_data(self, names: list[str], artists: list[str], timestamps: list[datetime], albums: list[str]) -> list[dict]:
    return [
      {
        "name": name,
        "artist": artists[i],
        "album": albums[i],
        "timestamp": timestamps[i]
      }
      for i, name in enumerate(names)
    ]

  def get_songs(self, pages: list[int]) -> list[dict]:
    songs = []
    for page_num in pages:
      if not is_cached(page_num, self.cache_folder):
        sleep(self.delay)

      soup = self.get_single_list_page_soup(page_num)
      songs.append(self.merge_data(*self.get_page_data(soup)))

    return flatten_list(songs)
