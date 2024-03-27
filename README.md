# Image Validation Automations

This workflow is a work in progress, but steps include:

* Sync files from Dropbox to Box and/or S3
* Read image files from Box/S3 directory
* Validate EXIF metadata
* Detect blurry images
* Write a report of the images in the directory

## Blur Dection

This is based on BlurDection2.

Blur detection works by using the total variance of the [Laplacian](https://docs.opencv.org/4.9.0/d5/db5/tutorial_laplace_operator.html) of an image to provide a quick and accurate method for scoring how blurry an image is. This is done by taking the difference between the mean pixel value in the original image and the mean pixel value in the blurred image, then squaring it and summing up all the values.

**The lower the score, the blurrier the image**

This algorithm depends on opencv and numpy.

### Local Setup

    pip install -r requirements.txt
    
### Running Locally

You can run the blur detection manually with. This will create a CSV report in the currently directory (`results.csv`) and is tuned specifically to run fast using [parallel processing](https://docs.python.org/3/library/multiprocessing.html).

    python process.py -i path/to/image_dir 
    
If  you need to run something that allows you to have more control (but is slower), you can run 

    python process_blur.py -i path/to/image_dir

For a full list of options, see `process.py --help` and `process_blur.py --help`.

This is based upon the blogpost [Blur Detection With Opencv](https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/) by Adrian Rosebrock.

## Finding Duplicates

In this processing, we add a method to add a hash of the image (pHash). Images that are the same will have the same hash and be added to the CSV. 

You can then use Pandas to find duplicates in your image directory.

```python
import pandas as pd

df = pd.read_csv('results.csv')
df1 = df[df.duplicated('hash', keep=False)].sort_values('hash')
df1.head()
```

### Alterative

* [difPy](https://difpy.readthedocs.io/en/v4.0.1/)