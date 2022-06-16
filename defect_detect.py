from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img
import numpy as np


img_path = r"D:\Programming\PROGRAMS\Proteus Projects\track\dataset\RANDOM\11.jpg"
image = load_img(img_path, target_size=(110, 55))
image = img_to_array(image)
image = preprocess_input(image)

data = []
data.append(image)
data = np.array(data, dtype="float32")

model = load_model('defect_detection.model')
model.load_weights('defect_detection_weights.h5')

pred = model.predict(data, batch_size=32)

(DEFECT, NODEFECT) = pred[0]

label = "Defect Detected" if DEFECT > NODEFECT else "No Defect Detected"

print(label)
print(pred)
hold = input()