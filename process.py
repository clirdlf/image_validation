#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ast import arg, mod, parse
from email.mime import image
from gettext import find
import re
import sys
import argparse
import logging
import pathlib
import os
import json
import time

from multiprocessing import Pool
from tracemalloc import start

import cv2
from numpy import fix
import pandas as pd

from blur_detection import estimate_blur
from blur_detection import fix_image_size
from blur_detection import pretty_blur_map
from blur_detection import p_hash

def parse_args():
    parser = argparse.ArgumentParser(description='Generate blur detection on a directory of images.')
    parser.add_argument('-i', '--images', required=True, type=str, nargs='+', default='images', help='Directory of images to blur detect.')
    # parser.add_argument('-s', '--save-path', type=str, help='File to save the output to save the results.')
    # parser.add_argument('-o', '--output-format', type=str, default='csv', choices=['csv', 'json'], help='Output format to save the results in.')
    # parser.add_argument('-t', '--threshold', type=float, default=100.0, help='Threshold for blur detection.')
    # parser.add_argument('-f', '--variable-size', action='store_true', help='Fix the image size.')
    # parser.add_argument('-l', '--logger', action='store_true', help='Log level the output.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output.')
    # parser.add_argument('-d', '--display-image', action='store_true', help='Display images')

    return parser.parse_args()

def find_images(image_paths, img_extensions=['png','jpg','jpeg','tif','tiff']):
    # Add in the capitalized extensions
    img_extensions += [i.upper() for i in img_extensions]
    
    for path in image_paths:
        path = pathlib.Path(path)

        # Check for single file
        if path.is_file():
            if path.suffix not in img_extensions:
                logging.info(f'{path.suffix} is not an image extension! skipping {path}')
                continue
            else:
                yield path

        # Check for directories
        if path.is_dir():
            for img_ext in img_extensions:
                yield from path.rglob(f'*{img_ext}')

def process_image(image_path):
    image = cv2.imread(str(image_path))

    threshold = 100.0

    if image is None:
        logging.warning(f'Warning: Could not load {image_path}. Skipping')
        return

    logging.info(f'Processing {image_path}')
    logging.info(f'Fixing image size of {image_path}')
    image = fix_image_size(image)

    phash = p_hash(image)
    blur_map, score, blurry = estimate_blur(image, threshold=threshold)
    logging.info(f'\tImage Path:{image_path} | score: {score} | blurry: {blurry} | hash: {phash}') 
    return {"filepath": image_path, "score": score, "blurry": blurry, "hash": phash } 

def convert_to_dataframe(results):
  """Converts the multiprocessing pool results to a pandas dataframe."""
  # Convert results to list of dictionaries
  data = [result.get() for result in results]
  return pd.DataFrame(data)

if __name__ == '__main__':
    assert sys.version_info >= (3, 10), 'Python version must be at least 3.10'
    args = parse_args()

    level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=level)

    #  fix_size = not args.variable_size
    fix_size = True

    core_count = os.cpu_count()
    pool = Pool(core_count) # TODO: Make this a parameter

    results = []
    start_time = time.time()

    for image_path in find_images(args.images):
        logging.info(f'Adding {image_path} to queue...')
        results.append(pool.apply_async(process_image, (image_path,)))

    pool.close()
    pool.join()

    end_time = time.time()

    df = convert_to_dataframe(results)
    
    df.to_csv('results.csv', index=False)
    print(df.head())

    blurry_count = len(df[df['blurry'] == True])
    total_count = len(df.index)
    blurry_percentage = round(blurry_count / total_count * 100, 2)
    total_time = round((end_time - start_time), 2)

    print(f'--- Image count: {total_count} ---')
    print(f'--- Found {blurry_count} blurry images ---')
    print(f'--- Percent blurry: {blurry_percentage}% ---')
    print(f'--- Total time taken: {total_time} seconds ---')
