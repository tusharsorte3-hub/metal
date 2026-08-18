import os
import io
import datetime

import numpy as np

from PIL import Image

from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

from flask_cors import CORS

import tensorflow as tf


# =========================
# PATHS
# =========================

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    ROOT,
    "backend",
    "models",
    "metalvision.keras"
)

FRONTEND_PATH = os.path.join(
    ROOT,
    "frontend"
)


# =========================
# FLASK
# =========================

app = Flask(
    __name__
)

CORS(app)


# =========================
# IMAGE SIZE
# =========================

IMG_SIZE = (
    224,
    224
)


# =========================
# LOAD MODEL
# =========================

model = None


if os.path.exists(
    MODEL_PATH
):

    print(
        "Loading AI model..."
    )

    model = tf.keras.models.load_model(
        MODEL_PATH
    )

    print(
        "AI model loaded."
    )

else:

    print()
    print(
        "WARNING:"
    )

    print(
        "No trained model found."
    )

    print(
        "Run:"
    )

    print(
        "python backend/train.py"
    )


# =========================
# PREDICTION
# =========================

def predict_image(
    image_bytes
):

    image = Image.open(
        io.BytesIO(
            image_bytes
        )
    ).convert(
        "RGB"
    )

    original_size = image.size

    image = image.resize(
        IMG_SIZE
    )

    image_array = np.asarray(
        image,
        dtype=np.float32
    )

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    prediction = model.predict(
        image_array,
        verbose=0
    )

    good_probability = float(
        prediction[0][0]
    )

    defective_probability = (
        1.0 -
        good_probability
    )

    if good_probability >= 0.5:

        result = "GOOD / USABLE"

        confidence = (
            good_probability
        )

    else:

        result = "BAD / DEFECTIVE"

        confidence = (
            defective_probability
        )

    return {

        "result":
            result,

        "good_probability":
            round(
                good_probability * 100,
                2
            ),

        "defective_probability":
            round(
                defective_probability * 100,
                2
            ),

        "confidence":
            round(
                confidence * 100,
                2
            ),

        "image_width":
            original_size[0],

        "image_height":
            original_size[1],

        "time":
            datetime.datetime.now().isoformat(),

        "warning":
            "Visual AI assessment only. Hidden/internal defects cannot be detected from a normal image."

    }


# =========================
# SERVER STATUS
# =========================

@app.route(
    "/api/status"
)
def status():

    return jsonify({

        "online":
            True,

        "model_loaded":
            model is not None

    })


# =========================
# IMAGE PREDICTION
# =========================

@app.route(
    "/api/predict",
    methods=["POST"]
)

def predict():

    if model is None:

        return jsonify({

            "error":
                "AI model is not trained. Run train.py first."

        }), 400


    if "image" not in request.files:

        return jsonify({

            "error":
                "No image received."

        }), 400


    try:

        image_file = request.files[
            "image"
        ]

        image_bytes = image_file.read()

        result = predict_image(
            image_bytes
        )

        return jsonify(
            result
        )

    except Exception as e:

        return jsonify({

            "error":
                str(e)

        }), 500


# =========================
# FRONTEND
# =========================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_PATH,
        "index.html"
    )


@app.route(
    "/<path:path>"
)

def frontend_files(
    path
):

    return send_from_directory(
        FRONTEND_PATH,
        path
    )


# =========================
# START
# =========================

if __name__ == "__main__":

    print()
    print("==============================")
    print(" METALVISION X SERVER")
    print("==============================")
    print()

    print(
        "Website:"
    )

    print(
        "http://localhost:5000"
    )

    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
