import json
import csv
from song import Song

class Exporter:
  def __init__(self, as_csv, as_json, as_datebase, file_name):
    self.as_csv = as_csv
    self.as_json = as_json
    self.as_datebase = as_datebase
    self.file_name = file_name

  def export_json(self, data: list[Song]) -> None:
    with open(f"{self.file_name}.json", "w", encoding="utf-8") as f:
      json.dump(data, f, default=str)
  
  def export_csv(self, data: list[Song]) -> None:
    with open(f"{self.file_name}.csv", "w", encoding="utf-8") as f:
      writer = csv.DictWriter(f, data[0].keys())
      writer.writeheader()
      writer.writerows(data)

  def export_database(self, data: list[Song]) -> None:
    raise Exception("Not supported")

  def export(self, data: list[Song]) -> None:
    if (self.as_json): self.export_json(data)
    if (self.as_csv): self.export_csv(data)
    if (self.as_datebase): self.export_database(data)