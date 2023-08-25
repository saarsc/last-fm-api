from datetime import datetime
from typing import TypedDict

class Song(TypedDict):
  name:str
  artist:str
  album:str
  timestamp:datetime