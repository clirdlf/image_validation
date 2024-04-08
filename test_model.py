from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
print("Loading model....")
model = load_model("model/keras_Model.h5", compile=False)

# Load the labels
print("Loading labels...")
class_names = open("model/labels.txt", "r").readlines()

# # CAMERA can be 0 or 1 based on default camera of your computer
# camera = cv2.VideoCapture(0)

# sample image
print("Loading images...")
image_with_target = 'training_data/target/5dd6f093a0a8b38e1993d74e53ed73b861d5f754.jpg'
image_without_target = 'training_data/no_target/4a289eb3fb33bc2ee2c96ec28f45d258cca0529b.jpg'

def score_image(image_path):
    image = cv2.imread(image_path)
    # resize to 224x224
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
    
    # cv2.imshow("Image", image)
    
    image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
    image = (image / 127.5) - 1
    
    prediction = model.predict(image)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]
    
    print("Class:", class_name[2:], end="")
    print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

score_image(image_with_target)
score_image(image_without_target)

