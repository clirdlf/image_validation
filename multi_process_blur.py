#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ast import arg, mod, parse
from gettext import find
import re
import sys
import argparse
import logging
import pathlib
import json
import time

from multiprocessing import Pool

import cv2
from numpy import fix
import pandas as pd

from blur_detection import estimate_blur
from blur_detection import fix_image_size
from blur_detection import pretty_blur_map

def is_image(filename):
  """Checks if the filename has a common image extension."""
  ext = os.path.splitext(filename)[1].lower()
  return ext in (".jpg", ".jpeg", ".png", ".bmp")

def estimate_blur(filepath):
  """Loads the image, calculates Laplacian variance for blur estimation,
  and returns a dictionary with blur value, filepath, and blur classification."""
  image = cv2.imread(filepath)
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  laplacian = cv2.Laplacian(gray, cv2.CV_64F).var()
  # Define a threshold for blur classification (adjust as needed)
  blur_threshold = 100
  is_blurry = laplacian < blur_threshold
  return {"blur": laplacian, "filepath": filepath, "is_blurry": is_blurry}

def process_directory_s(dirpath):
  results = []

  for filename in os.listdir(dirpath):
    filepath = os.path.join(dirpath, filename)
    if os.path.isdir(filepath):
      print(f"Scanning {filepath}  for images")
      process_directory(filepath)
    elif is_image(filename):
      print(f"Processing {filename}")
      results.append(estimate_blur(filepath))

  return results
    

def process_directory(dirpath):
  """Recursively walks through the directory, finds images,
  uses multiprocessing pool to estimate blur for each image,
  and collects results in a pandas dataframe."""
  core_count = os.cpu_count() - 2
  pool = Pool(core_count) #
  results = []
  for filename in os.listdir(dirpath):
    filepath = os.path.join(dirpath, filename)
    if os.path.isdir(filepath):
      print("Scanning {} for images").format(filepath)
      process_directory(filepath)  # Recursively call for subdirectories
    elif is_image(filename):
      print(f"Adding {filename} to the queue")
      results.append(pool.apply_async(estimate_blur, (filepath,)))
  pool.close()
  pool.join()

  return results

def convert_to_dataframe(results):
  """Converts the multiprocessing pool results to a pandas dataframe."""
  # Convert results to list of dictionaries
  results = [result.get() for result in results]
  return pd.DataFrame(results)

def convert_to_df(results):
  return pd.DataFrame(results)

def calc_improvement(parallel_time, serial_time):
  return (serial_time - parallel_time)/serial_time * 100

if __name__ == "__main__":
  # Replace 'path/to/your/directory' with the actual directory path
  print("Parrallelized image processing...")
#   process_directory("images")
  start_time = time.time()
  report = process_directory("images")
  df = convert_to_dataframe(report)
  end_time = time.time()
  print(df.head())
  parallel_time = end_time - start_time
  print("--- %s seconds ---" % (parallel_time))

  print("Serialized image processing...")
  start_time = time.time()
  report = process_directory_s("images")
  df = convert_to_df(report)
  end_time = time.time()
  print(df.head())
  serial_time = end_time - start_time
  print("--- %s seconds ---" % (serial_time))

  print("---")
  print(f"Improvement using multiprocessing: {calc_improvement(parallel_time, serial_time):.2f}%")

