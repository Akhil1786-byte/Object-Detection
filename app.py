from flask import(
    Flask, 
    redirect,
    url_for,
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

    if request.method == "POST":

        if "video" not in request.files:
            return redirect(url_for("index"))

        video = request.files["video"]

        if video.filename == "":
            return redirect(url_for("index"))

        filename = secure_filename(
            video.filename
        )

        current_video_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        video.save(
            current_video_path
        )

        current_output_filename = (
            f"output_{int(time.time())}.mp4"
        )

        return redirect(
            url_for("index")
        )

    return render_template(
        "index.html",
        video_uploaded=current_video_path is not None,
        timestamp=time.time()
    )
# =========================================
# VIDEO STREAM
# =========================================

@app.route("/video_feed")
def video_feed():

    global current_video_path
    global current_output_filename

    print("VIDEO FEED CALLED")

    if current_video_path is None:

        print("No video uploaded")

        return (
            "No video uploaded",
            400
        )

    if current_output_filename is None:

        print("No output filename")

        return (
            "No output filename",
            400
        )

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

    if current_output_filename is None:

        return (
            "No processed video available",
            400
        )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        current_output_filename
    )

    if not os.path.exists(
        output_path
    ):

        return (
            "Output file not found",
            404
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
