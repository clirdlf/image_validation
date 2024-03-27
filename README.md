# IJA Automations

This workflow is a work in progress, but steps include:

* Sync files from NER Dropbox to CLIR Box and/or S3
* Read image files from Box/S3 directory
* Validate EXIF metadata
* Detect blurry images
* Write a report of the images in the directory

## Blur Dection

This is based on BlurDection2.

Blur detection works by using the total variance of the laplacian of an image to provide a quick and accurate method for scoring how blurry an image is. This is done by taking the difference between the mean pixel value in the original image and the mean pixel value in the blurred image, then squaring it and summing up all the values. The higher the variance of the laplacian, the more blurry the image.

This algorithm depends on opencv and numpy.

### Local Setup

    pip install -r requirements.txt
    
### Running Locally

This repository has a script, `process_blur.py` that runs on a single image, or directory of images. The blur detection is highly dependent on the size of the image being processed. To get consistent scores we'll need to fix the image size to HD. To disable this, use the `--variable-size` flag.

```bash
# run on a single image

# run on a directory of images
python process_blur.py -i input_directory/ 
```

Reporting can be in CSV or JSON and saved.

```bash
# Output CSV
python process_blur.py -i input_directory/ -o csv

# Output JSON
python process_blur.py -i input_directory/ -o json

# Save CSV
python process_blur.py -i input_directory/ -o csv -s report.csv

# Save JSON
python process_blur.py -i input_directory/ -o json -s report.json
```

The output has information about how blurry an image is; the higher the value, the less blurry the image. 

```json
{
    "images": [
        "images"
    ],
    "threshold": 100.0,
    "blurry_counts": {
        "true": 23,
        "false": 3
    },
    "fix_size": true,
    "results": [
        {
            "input_path": "images/IMG_0014.JPG",
            "score": 63.529971074944825,
            "blurry": true
        },
        {
            "input_path": "images/IMG_0002.JPG",
            "score": 470.91608880174437,
            "blurry": false
        },
    ]
}
```