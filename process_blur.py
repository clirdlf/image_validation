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

import cv2
from numpy import fix
import pandas as pd

from blur_detection import estimate_blur
from blur_detection import fix_image_size
from blur_detection import pretty_blur_map

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

def parse_args():
    parser = argparse.ArgumentParser(description='Generate blur detection on a directory of images.')
    parser.add_argument('-i', '--images', type=str, nargs='+', default='images', help='Directory of images to blur detect.')
    parser.add_argument('-s', '--save-path', type=str, help='File to save the output to save the results.')
    parser.add_argument('-o', '--output-format', type=str, default='csv', choices=['csv', 'json'], help='Output format to save the results in.')
    parser.add_argument('-t', '--threshold', type=float, default=100.0, help='Threshold for blur detection.')
    parser.add_argument('-f', '--variable-size', action='store_true', help='Fix the image size.')
    parser.add_argument('-l', '--logger', action='store_true', help='Log the output.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output.')
    parser.add_argument('-d', '--display-image', action='store_true', help='Display images')

    return parser.parse_args()

if __name__ == '__main__':
    assert sys.version_info >= (3, 10), 'Python version must be at least 3.10'
    args = parse_args()

    level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=level)

    fix_size = not args.variable_size

    results = []

    for image_path in find_images(args.images):
        image = cv2.imread(str(image_path))

        if image is None:
            logging.warning(f'Warning: Could not load {image_path}. Skipping')
            continue
        logging.info(f'Processing {image_path}')

        if fix_size:
            logging.info(f'Fixing size of {image_path}')
            image = fix_image_size(image)
        else:
            logging.warning('Not normalizing image size for consistent scoring.')
        
        blur_map, score, blurry = estimate_blur(image, threshold=args.threshold)
        logging.info(f'\tImage Path:{image_path} | score: {score} | blurry: {blurry}')

        results.append({'input_path': str(image_path), 'score': score, 'blurry': blurry})

        if args.display_image:
            cv2.imshow('Image', image)
            cv2.imshow('Blur Map', pretty_blur_map(blur_map))

            if cv2.waitKey(0) == ord('q'):
                logging.info('Quitting')
                exit()
    
    df = pd.DataFrame(results)
    df.sort_values(by='input_path', ascending=True, inplace=True)
    
    if args.output_format == 'csv':
        if(args.save_path):
            logging.info('Writing results to csv file.')
            df.to_csv(args.save_path, index=False)
        else:
            print(df.head())
        
    elif args.output_format == 'json':
        blurry_counts = df['blurry'].value_counts()

        data = {
            'images': args.images, 
            'threshold': args.threshold, 
            'blurry_counts': blurry_counts.to_dict(),
            'fix_size': fix_size, 
            'results': results
        }
       
        if(args.save_path):
            logging.info(f'saving data to {args.save_path}')

            with open(args.save_path, 'w') as result_file:
                json.dump(data, result_file, indent=4)
        else:
            print(json.dumps(data, indent=4))
    else:
        raise ValueError('Invalid output format.')