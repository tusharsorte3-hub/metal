import os
import tensorflow as tf

from tensorflow.keras import layers
from tensorflow.keras import models
from tensorflow.keras.applications import MobileNetV2

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATASET = os.path.join(ROOT, "dataset")

MODEL_DIR = os.path.join(
    ROOT,
    "backend",
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "metalvision.keras"
)

IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 15

os.makedirs(MODEL_DIR, exist_ok=True)

print()
print("==============================")
print(" METALVISION X AI TRAINING")
print("==============================")
print()

train_data = tf.keras.utils.image_dataset_from_directory(

    DATASET,

    validation_split=0.20,

    subset="training",

    seed=123,

    image_size=IMG_SIZE,

    batch_size=BATCH_SIZE,

    label_mode="binary"
)

validation_data = tf.keras.utils.image_dataset_from_directory(

    DATASET,

    validation_split=0.20,

    subset="validation",

    seed=123,

    image_size=IMG_SIZE,

    batch_size=BATCH_SIZE,

    label_mode="binary"
)

print()

print(
    "Classes:",
    train_data.class_names
)

if set(train_data.class_names) != {"bad", "good"}:

    raise Exception(
        "Dataset must contain exactly:"
        " dataset/good and dataset/bad"
    )

AUTOTUNE = tf.data.AUTOTUNE

train_data = train_data.prefetch(
    AUTOTUNE
)

validation_data = validation_data.prefetch(
    AUTOTUNE
)

# -------------------------
# DATA AUGMENTATION
# -------------------------

augmentation = tf.keras.Sequential([

    layers.RandomFlip(
        "horizontal"
    ),

    layers.RandomRotation(
        0.05
    ),

    layers.RandomZoom(
        0.10
    ),

    layers.RandomContrast(
        0.10
    )

])

# -------------------------
# BASE MODEL
# -------------------------

base_model = MobileNetV2(

    input_shape=(
        224,
        224,
        3
    ),

    include_top=False,

    weights="imagenet"
)

base_model.trainable = False

# -------------------------
# MODEL
# -------------------------

inputs = layers.Input(
    shape=(224, 224, 3)
)

x = augmentation(inputs)

x = tf.keras.applications.mobilenet_v2.preprocess_input(
    x
)

x = base_model(
    x,
    training=False
)

x = layers.GlobalAveragePooling2D()(x)

x = layers.Dropout(
    0.25
)(x)

outputs = layers.Dense(
    1,
    activation="sigmoid"
)(x)

model = models.Model(
    inputs,
    outputs
)

model.compile(

    optimizer=tf.keras.optimizers.Adam(
        learning_rate=0.001
    ),

    loss="binary_crossentropy",

    metrics=["accuracy"]

)

model.summary()

# -------------------------
# TRAIN
# -------------------------

early_stop = tf.keras.callbacks.EarlyStopping(

    monitor="val_loss",

    patience=4,

    restore_best_weights=True

)

history = model.fit(

    train_data,

    validation_data=validation_data,

    epochs=EPOCHS,

    callbacks=[
        early_stop
    ]

)

# -------------------------
# SAVE
# -------------------------

model.save(
    MODEL_PATH
)

print()
print("==============================")
print(" TRAINING COMPLETE")
print("==============================")
print()

print(
    "Model saved at:"
)

print(
    MODEL_PATH
)

print()
print("You can now start app.py")
