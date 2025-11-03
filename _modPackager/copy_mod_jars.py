

import os, sys, time
from pathlib import Path # path tool
import shutil # file tool


def copy_mod_jars (p_jars:Path, jar_paths:list[str]):
  for path in jar_paths:
      try:
          res = shutil.copy(path, p_jars)
      except (PermissionError) as e:#srcfileが空欄または無効な値
          print(e)