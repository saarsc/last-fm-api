import csv
import json
from song import Song
from datetime import datetime
from contextlib import contextmanager

class Importer:
  def __init__(self, as_json=True , as_csv=False, filename="out") -> None:
    self.as_csv: bool = as_csv
    self.as_json: bool = as_json
    self.filename: str = filename
    self.data: list[Song] = []
    try:
      self.import_data()
    except FileNotFoundError:
      pass

  def import_csv(self) -> list[Song]:
    with self.data_file() as f:
      self.data = list(csv.DictReader(f, ))
      
  def import_json(self):
    with self.data_file() as f:
      self.data = json.load(f)

  def import_db(self):
    raise NotImplementedError

  def import_data(self) -> list[Song]:
    if self.as_csv:
      self.import_csv()
    
    if self.as_json:
      return self.import_json()
  
  @contextmanager
  def data_file(self):
    with open(f"{self.filename}.json", encoding="utf-8") as f:
      yield f

  @property
  def latest_date(self):
    return max(
      self.data, 
      key=lambda scrobble: datetime.strptime(scrobble["timestamp"], "%Y-%m-%d %H:%M:%S")
    )["timestamp"].split(" ")[0]