from flask import (
    Flask,
    render_template,
    Response,
    request,
    send_file
)

import os
import time

from werkzeug.utils import secure_filename

from detect_video import generate_frames

# =========================================
# FLASK APP
# =========================================

app = Flask(__name__)

# =========================================
# FOLDERS
# =========================================

UPLOAD_FOLDER = "input_videos"

OUTPUT_FOLDER = "output_videos"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

# =========================================
# GLOBAL VARIABLES
# =========================================

current_video_path = None

current_output_filename = None

# =========================================
# HOME PAGE
# =========================================

@app.route("/", methods=["GET", "POST"])

def index():

    global current_video_path
    global current_output_filename

    # =====================================
    # HANDLE VIDEO UPLOAD
    # =====================================

    if request.method == "POST":

        video = request.files["video"]

        if video:

            # =================================
            # SAFE FILE NAME
            # =================================

            filename = secure_filename(
                video.filename
            )

            # =================================
            # INPUT VIDEO PATH
            # =================================

            current_video_path = os.path.join(

                UPLOAD_FOLDER,

                filename

            )

            # =================================
            # SAVE INPUT VIDEO
            # =================================

            video.save(
                current_video_path
            )

            # =================================
            # UNIQUE OUTPUT FILE
            # =================================

            current_output_filename = (

                f"output_{int(time.time())}.mp4"

            )

    return render_template(

        "index.html",

        video_uploaded=
        current_video_path is not None,

        timestamp=
        time.time()

    )

# =========================================
# VIDEO STREAM
# =========================================

@app.route("/video_feed")

def video_feed():

    global current_video_path
    global current_output_filename

    output_path = os.path.join(

        OUTPUT_FOLDER,

        current_output_filename

    )

    return Response(

        generate_frames(

            current_video_path,

            output_path

        ),

        mimetype=
        "multipart/x-mixed-replace; boundary=frame"

    )

# =========================================
# DOWNLOAD VIDEO
# =========================================

@app.route("/download")

def download_video():

    global current_output_filename

    output_path = os.path.join(

        OUTPUT_FOLDER,

        current_output_filename

    )

    return send_file(

        output_path,

        as_attachment=True

    )

# =========================================
# RUN APP
# =========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
