import os
from tqdm.auto import tqdm
import random
import json

import tensorflow as tf
from tensorflow import keras

import keras_cv
from keras_cv import bounding_box
from keras_cv import visualization

SPLIT_RATIO = 0.1
BATCH_SIZE = 160
LEARNING_RATE = 0.024
GLOBAL_CLIPNORM = 10.0

dataset_dir = "/home/droneai/rad_photo_custom/yolo_labeled_files"
model_store_dir = "/home/denys/Downloads/Models_by_epochs"

class_ids = [
    "With_Radiation_sign",
    "Without_Radiation_sign",
    "Radiation_sign"
]

class_mapping = dict(zip(range(len(class_ids)), class_ids))
name2classID = {value:key for key,value in class_mapping.items()}

txt_files = []

for r, _, f in os.walk(dataset_dir):
    for txt_filename in f:
        txt_files.append(os.path.join(r, txt_filename))
txt_files = sorted(txt_files)
random.seed(10)
random.shuffle(txt_files)

def parse_annotation(txt_file):

    image_path = txt_file.split("/")
    image_path[-2] = "imgs"
    image_path[-1] = image_path[-1][:-4] + ".jpg"
    image_path = "/".join(image_path)

    boxes = []
    class_ids = []
    with open(txt_file) as file:

        for line in file:
            lineSplit = line.split()
            print(lineSplit)
            box = lineSplit[1:]
            box = [640*float(coor) for coor in box]

            # correct from center to edge of the box
            box[0] -= box[2]/2
            box[1] -= box[3]/2

            boxes.append(box)


            class_ids.append(lineSplit[0])


    return image_path, boxes, class_ids


image_paths = []
bbox = []
classes = []
for txt_file in tqdm(txt_files):
    image_path, boxes, class_ids = parse_annotation(txt_file)
    image_paths.append(image_path)
    bbox.append(boxes)
    classes.append(class_ids)

print("Lenght of imgaes list",  len(image_paths))
print("Lenght of bbox list",    len(bbox))
print("Lenght of classes list", len(classes))

bbox = tf.ragged.constant(bbox)
classes = tf.ragged.constant(classes)
image_paths = tf.ragged.constant(image_paths)

data = tf.data.Dataset.from_tensor_slices((image_paths, classes, bbox))

# Determine the number of validation samples
num_valtest = int(len(txt_files) * SPLIT_RATIO)

# Split the dataset into train and validation sets
valtest_data = data.take(num_valtest+num_valtest)

val_data = valtest_data.take(num_valtest)
test_data = valtest_data.skip(num_valtest)

train_data = data.skip(num_valtest+num_valtest)

def load_image(image_path):
    image = tf.io.read_file(image_path)
    image = tf.image.decode_png(image, channels=3)
    return image


def load_dataset(image_path, classes, bbox):
    # Read Image
    image = load_image(image_path)
    bounding_boxes = {
        "classes": tf.cast(classes, dtype=tf.float32),
        "boxes": bbox,
    }
    return {"images": tf.cast(image, tf.float32), "bounding_boxes": bounding_boxes}
augmenter = keras.Sequential(
    layers=[
        keras_cv.layers.RandomFlip(mode="horizontal", bounding_box_format="xywh"),
        # keras_cv.layers.RandomShear( # crosscheck with visualisation shows that shear make only whorse
        #     x_factor=0.2, y_factor=0.2, bounding_box_format="xywh"
        # ),
        keras_cv.layers.JitteredResize(
            target_size=(640, 640), scale_factor=(1, 1), bounding_box_format="xywh"
        ),
    ]
)

train_ds = train_data.map(load_dataset, num_parallel_calls=tf.data.AUTOTUNE)
train_ds = train_ds.shuffle(BATCH_SIZE * 4)
train_ds = train_ds.ragged_batch(BATCH_SIZE, drop_remainder=True)
train_ds = train_ds.map(augmenter, num_parallel_calls=tf.data.AUTOTUNE)

resizing = keras_cv.layers.JitteredResize(
    target_size=(640, 640),
    scale_factor=(1, 1),
    bounding_box_format="xywh",
)

val_ds = val_data.map(load_dataset, num_parallel_calls=tf.data.AUTOTUNE)
val_ds = val_ds.shuffle(BATCH_SIZE * 4)
val_ds = val_ds.ragged_batch(BATCH_SIZE, drop_remainder=True)
val_ds = val_ds.map(resizing, num_parallel_calls=tf.data.AUTOTUNE)

def visualize_dataset(inputs, value_range, rows, cols, bounding_box_format):

    inputs = next(iter(inputs.take(1)))
    images, bounding_boxes = inputs["images"], inputs["bounding_boxes"]
    visualization.plot_bounding_box_gallery(
        images,
        value_range=value_range,
        rows=rows,
        cols=cols,
        y_true=bounding_boxes,
        scale=5,
        font_scale=0.7,
        bounding_box_format=bounding_box_format,
        class_mapping=class_mapping,
    )


visualize_dataset(
    train_ds, bounding_box_format="xywh", value_range=(0, 255), rows=2, cols=2
)

visualize_dataset(
    val_ds, bounding_box_format="xywh", value_range=(0, 255), rows=2, cols=2
)
def dict_to_tuple(inputs):
    return inputs["images"], bounding_box.to_dense(inputs["bounding_boxes"], max_boxes=32)


train_ds = train_ds.map(dict_to_tuple, num_parallel_calls=tf.data.AUTOTUNE)
train_ds = train_ds.prefetch(tf.data.AUTOTUNE)

val_ds = val_ds.map(dict_to_tuple, num_parallel_calls=tf.data.AUTOTUNE)
val_ds = val_ds.prefetch(tf.data.AUTOTUNE)

yolo = keras_cv.models.YOLOV8Detector.from_preset(
    "mobilenet_v3_small_imagenet",
    bounding_box_format="xywh",
    num_classes=len(class_mapping),
    input_shape = (640, 640, 3),
    load_weights=True)

isLayersTrainable = False

for layer in yolo.layers:

    if layer.name == "tf.concat_5" and not isLayersTrainable:
        isLayersTrainable = True

    if isLayersTrainable:
        layer.trainable=True
    else:
        layer.trainable=False

optimizer = tf.keras.optimizers.Adam(
    learning_rate=LEARNING_RATE,
    global_clipnorm=GLOBAL_CLIPNORM,
)

yolo.compile(
    optimizer=optimizer, classification_loss="binary_crossentropy", box_loss="ciou"
)

class EvaluateCOCOMetricsCallback(keras.callbacks.Callback):
    def __init__(self, data, save_dir):
        super().__init__()
        self.data = data
        self.metrics = keras_cv.metrics.BoxCOCOMetrics(
            bounding_box_format="xywh",
            evaluate_freq=1e9,
        )

        self.save_dir = save_dir

    def on_epoch_end(self, epoch, logs):
        self.metrics.reset_state()
        for batch in self.data:
            images, y_true = batch[0], batch[1]
            y_pred = self.model.predict(images, verbose=0)
            self.metrics.update_state(y_true, y_pred)

        metrics = self.metrics.result(force=True)
        logs.update(metrics)

        # save logs
        with open(os.path.join(self.save_dir, f"epoch_{epoch}_logs.txt"), "w") as file:
            for key, value in logs.items():

                if isinstance(value, tf.Tensor):
                    file.write(key + ":" + str(value.numpy()) + "\n")
                else:
                    file.write(key + ":" + str(value) + "\n")


        # save model
        self.model.save(os.path.join(self.save_dir, f"epoch_{epoch}_model.keras"))

        return logs
history = yolo.fit(
    train_ds,
    validation_data=val_ds,
    epochs=50,
    callbacks=[EvaluateCOCOMetricsCallback(val_ds, model_store_dir)],
)
filenames = os.listdir(model_store_dir)
filenames = [filename for filename in filenames if ".txt" in filename]

logs = {}

with open(os.path.join(model_store_dir, filenames[0]), "r") as file:

    for line in file:
        key = line.split(":")[0]

        logs[key] = []

for epoch in range(len(filenames)):

    filename = f"epoch_{epoch}_logs.txt"

    with open(os.path.join(model_store_dir, filename), "r") as file:

        for line in file:

            key, value = line.split(":")
            value = float(value)

            logs[key].append(value)

epochs  = [i+1 for i in range(len(filenames))]

import matplotlib.pyplot as plt

for key, value in logs.items():

    plt.figure()
    plt.plot(epochs[3:], value[3:])
    plt.xlabel("epoch")
    plt.ylabel(key)

def evaluateCocoMetrics(model, data):

    boxCOCOMetrics = keras_cv.metrics.BoxCOCOMetrics(
        bounding_box_format="xywh",
        evaluate_freq=1e9,
    )

    boxCOCOMetrics.reset_state()

    numOfSteps = tf.data.experimental.cardinality(data).numpy()

    for i,batch in enumerate(data):
        print(f"\r Processing step {i+1}/{numOfSteps}", end="")
        images, y_true = batch[0], batch[1]
        y_pred = model.predict(images, verbose=0)
        boxCOCOMetrics.update_state(y_true, y_pred)
    print("\n")


    logs = boxCOCOMetrics.result(force=True)

    return logs
test_ds = test_data.map(load_dataset, num_parallel_calls=tf.data.AUTOTUNE)
test_ds = test_ds.shuffle(BATCH_SIZE * 4)
test_ds = test_ds.ragged_batch(BATCH_SIZE, drop_remainder=True)
test_ds = test_ds.map(resizing, num_parallel_calls=tf.data.AUTOTUNE)

test_ds = test_ds.map(dict_to_tuple, num_parallel_calls=tf.data.AUTOTUNE)
test_ds = test_ds.prefetch(tf.data.AUTOTUNE)

BEST_EPOCH = 48

model_path = os.path.join(model_store_dir, f"epoch_{BEST_EPOCH}_model.keras")
yolo_best = tf.keras.models.load_model(model_path)

yolo_best.compile(
    optimizer=optimizer, classification_loss="binary_crossentropy", box_loss="ciou"
)

logs = yolo_best.evaluate(test_ds)
logs = {"loss": logs[0],
        "box_loss": logs[1],
        "class_loss": logs[2]
}

logs.update( evaluateCocoMetrics(yolo_best, test_ds) )

print("{:<27} {:<10}".format('Metric','Value'))

for key, value in logs.items():
    if isinstance(value, tf.Tensor):
        print("{:<27} {:<10}".format(key, value.numpy()))
    else:
        print("{:<27} {:<10}".format(key, value))

def visualize_detections(model, dataset, bounding_box_format):
    images, y_true = next(iter(dataset.take(1)))
    y_pred = model.predict(images)
    y_pred = bounding_box.to_ragged(y_pred)
    visualization.plot_bounding_box_gallery(
        images,
        value_range=(0, 255),
        bounding_box_format=bounding_box_format,
        y_true=y_true,
        y_pred=y_pred,
        scale=4,
        rows=2,
        cols=2,
        show=True,
        font_scale=0.7,
        class_mapping=class_mapping,
    )


visualize_detections(yolo_best, dataset=val_ds, bounding_box_format="xywh")

train_image_paths = train_data.map(lambda image_path, _, __: image_path)
datasetFileTrain = os.path.join(model_store_dir, "trainDatasetFile.txt")

with open(datasetFileTrain, "w") as trainDataFile:
    for image_path in train_image_paths:
            trainDataFile.write(image_path.numpy().decode('utf-8') + "\n")

##########################################################################

val_image_paths = val_data.map(lambda image_path, _, __: image_path)
datasetFileVal = os.path.join(model_store_dir, "valDatasetFile.txt")

with open(datasetFileVal, "w") as valDataFile:
    for image_path in val_image_paths:
            valDataFile.write(image_path.numpy().decode('utf-8') + "\n")

#########################################################################

test_image_paths = test_data.map(lambda image_path, _, __: image_path)
datasetFileTest = os.path.join(model_store_dir, "testDatasetFile.txt")

with open(datasetFileTest, "w") as testDataFile:
    for image_path in test_image_paths:
            testDataFile.write(image_path.numpy().decode('utf-8') + "\n")