let selectedFile = null;


const imageInput =
    document.getElementById(
        "imageInput"
    );


const preview =
    document.getElementById(
        "preview"
    );


const analyzeButton =
    document.getElementById(
        "analyzeButton"
    );


const result =
    document.getElementById(
        "result"
    );


const dropZone =
    document.getElementById(
        "dropZone"
    );


// ===========================
// SERVER STATUS
// ===========================

async function checkServer() {

    try {

        const response =
            await fetch(
                "/api/status"
            );

        const data =
            await response.json();


        document.getElementById(
            "systemStatus"
        ).textContent =
            data.model_loaded
            ? "● AI ENGINE ONLINE"
            : "● MODEL NOT TRAINED";


        document.getElementById(
            "systemStatus"
        ).style.color =
            data.model_loaded
            ? "#45ff9b"
            : "#ffb84d";


        document.getElementById(
            "modelStatus"
        ).textContent =
            data.model_loaded
            ? "TRAINED"
            : "NOT TRAINED";

    }

    catch(error) {

        document.getElementById(
            "systemStatus"
        ).textContent =
            "● SERVER OFFLINE";

        document.getElementById(
            "systemStatus"
        ).style.color =
            "#ff416d";

    }

}


checkServer();


// ===========================
// UPLOAD
// ===========================

function openUpload() {

    imageInput.click();

}


imageInput.addEventListener(
    "change",
    function(event) {

        if (
            event.target.files.length
        ) {

            selectFile(
                event.target.files[0]
            );

        }

    }
);


// ===========================
// DRAG DROP
// ===========================

dropZone.addEventListener(
    "dragover",
    function(event) {

        event.preventDefault();

    }
);


dropZone.addEventListener(
    "drop",
    function(event) {

        event.preventDefault();

        if (
            event.dataTransfer.files.length
        ) {

            selectFile(
                event.dataTransfer.files[0]
            );

        }

    }
);


// ===========================
// SELECT IMAGE
// ===========================

function selectFile(file) {

    if (
        !file.type.startsWith(
            "image/"
        )
    ) {

        alert(
            "Please select an image."
        );

        return;

    }


    selectedFile = file;


    preview.src =
        URL.createObjectURL(
            file
        );


    preview.style.display =
        "block";


    result.textContent =
        "IMAGE READY";


    result.className =
        "result";


    analyzeButton.disabled =
        false;

}


// ===========================
// ANALYZE
// ===========================

async function analyzeImage() {

    if (!selectedFile) {

        return;

    }


    analyzeButton.disabled =
        true;


    result.textContent =
        "INITIALIZING AI ENGINE...";


    await wait(600);


    result.textContent =
        "EXTRACTING FEATURES...";


    await wait(600);


    result.textContent =
        "COMPARING TRAINING PHOTOS...";


    await wait(600);


    const formData =
        new FormData();


    formData.append(
        "image",
        selectedFile
    );


    try {

        const response =
            await fetch(
                "/api/predict",
                {
                    method:
                    "POST",

                    body:
                    formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error
            );

        }


        showResult(data);

    }

    catch(error) {

        result.className =
            "result bad";

        result.textContent =
            error.message;

    }


    analyzeButton.disabled =
        false;

}


// ===========================
// RESULT
// ===========================

function showResult(data) {

    const good =
        data.result.startsWith(
            "GOOD"
        );


    result.className =
        good
        ? "result good"
        : "result bad";


    result.innerHTML = `

        ${good ? "✓" : "✕"}

        ${data.result}

        <br>

        <small>

        CONFIDENCE:
        ${data.confidence}%

        <br>

        GOOD:
        ${data.good_probability}%

        &nbsp;

        BAD:
        ${data.defective_probability}%

        </small>

        <p>

        ${data.warning}

        </p>

    `;


    // Voice output

    if (
        "speechSynthesis"
        in window
    ) {

        speechSynthesis.cancel();


        const speech =
            new SpeechSynthesisUtterance(

                good

                ?

                `Inspection completed. The metal part appears good. Estimated confidence ${data.confidence} percent.`

                :

                `Warning. The metal part appears defective. Estimated confidence ${data.confidence} percent.`

            );


        speechSynthesis.speak(
            speech
        );

    }

}


// ===========================
// ESP32 CAMERA
// ===========================

function scrollCamera() {

    document
        .getElementById(
            "cameraSection"
        )
        .scrollIntoView({
            behavior:
            "smooth"
        });

}


function connectCamera() {

    let ip =
        document
        .getElementById(
            "cameraIP"
        )
        .value
        .trim();


    ip =
        ip.replace(
            /\/$/,
            ""
        );


    if (!ip) {

        alert(
            "Enter ESP32-CAM IP."
        );

        return;

    }


    document
        .getElementById(
            "cameraStream"
        )
        .src =
        ip + "/stream";

}


async function captureCamera() {

    let ip =
        document
        .getElementById(
            "cameraIP"
        )
        .value
        .trim();


    ip =
        ip.replace(
            /\/$/,
            ""
        );


    if (!ip) {

        alert(
            "Enter ESP32-CAM IP."
        );

        return;

    }


    try {

        result.textContent =
            "CAPTURING ESP32-CAM IMAGE...";


        const response =
            await fetch(
                ip + "/capture"
            );


        if (!response.ok) {

            throw new Error(
                "Camera capture failed."
            );

        }


        const blob =
            await response.blob();


        selectedFile =
            new File(
                [blob],
                "esp32cam.jpg",
                {
                    type:
                    "image/jpeg"
                }
            );


        preview.src =
            URL.createObjectURL(
                blob
            );


        preview.style.display =
            "block";


        analyzeButton.disabled =
            false;


        await analyzeImage();

    }

    catch(error) {

        result.className =
            "result bad";

        result.textContent =
            error.message;

    }

}


// ===========================
// WAIT
// ===========================

function wait(ms) {

    return new Promise(
        resolve =>
        setTimeout(
            resolve,
            ms
        )
    );

}
