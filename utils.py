import urllib.parse
import itertools
import os
import shutil

def split_to_chunks(list: list, chunk_size: int):
  for i in range(0, len(list), chunk_size):
    yield list[i:i + chunk_size]


def url_decode(string: str) -> str:
  return urllib.parse.unquote_plus(string)


def flatten_list(list_of_lists: list[list]) -> list:
  return list(itertools.chain(*list_of_lists))


def read_from_cache(file_name: str, cache_folder: str):
  with open(f"{cache_folder}/{file_name}", encoding="utf-8") as f:
    return f.read()


def write_to_cache(file_name: str, cache_folder: str, data):
  if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

  with open(f"{cache_folder}/{file_name}", "w", encoding="utf-8") as f:
    f.write(data)


def is_cached(file_name, cache_folder):
  return os.path.exists(f"{cache_folder}/{file_name}.html")

def reset_cache(cache_folder: str):
  shutil.rmtree(cache_folder)
  os.makedirs(cache_folder)
