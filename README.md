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
python process_blur.py --image /path/to/image.jpg
```