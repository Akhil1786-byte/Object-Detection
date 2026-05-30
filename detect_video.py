import cv2
import numpy as np
import os

from ultralytics import YOLO

# =========================================
# LOAD MODEL
# =========================================

print("Loading YOLO Model...")

model = YOLO("yolov8n.pt")

print("Model Loaded!")

# =========================================
# PANEL WIDTH
# =========================================

panel_width = 250

# =========================================
# CLASS COLORS
# =========================================

class_colors = {

    "person": (0, 255, 0),
    "car": (255, 0, 0),
    "truck": (0, 0, 255),
    "bus": (255, 255, 0),
    "motorcycle": (255, 0, 255),
    "bicycle": (0, 255, 255)

}

# =========================================
# GENERATE FRAMES
# =========================================

def generate_frames(

    video_path,

    output_path

):

    # =====================================
    # VIDEO
    # =====================================

    cap = cv2.VideoCapture(
        video_path
    )

    # =====================================
    # VIDEO PROPERTIES
    # =====================================

    width = int(
        cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    fps = int(
        cap.get(cv2.CAP_PROP_FPS)
    )

    combined_width = width + panel_width

    # =====================================
    # SAVE OUTPUT VIDEO
    # =====================================

    fourcc = cv2.VideoWriter_fourcc(
        *'mp4v'
    )

    out = cv2.VideoWriter(

        output_path,

        fourcc,

        fps,

        (combined_width, height)

    )

    # =====================================
    # RESET COUNTERS
    # =====================================

    id_name_map = {}

    class_counters = {}

    counted_ids = {}

    object_counts = {}

    # =====================================
    # PROCESS VIDEO
    # =====================================

    while True:

        success, frame = cap.read()

        if not success:
            break

        # =================================
        # FRAME SIZE
        # =================================

        height, width, _ = frame.shape

        # =================================
        # YOLO TRACKING
        # =================================

        results = model.track(

            frame,

            persist=True,

            tracker="bytetrack.yaml",

            conf=0.5,

            iou=0.5,

            verbose=False,

            classes=[0, 1, 2, 3, 5, 7]

        )

        # =================================
        # DRAW DETECTIONS
        # =================================

        if results[0].boxes is not None:

            for box in results[0].boxes:

                # =========================
                # SKIP IF NO TRACK ID
                # =========================

                if box.id is None:
                    continue

                # =========================
                # BOX COORDINATES
                # =========================

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                # =========================
                # FILTER SMALL DETECTIONS
                # =========================

                box_width = x2 - x1
                box_height = y2 - y1

                if (
                    box_width < 30 or
                    box_height < 30
                ):
                    continue

                # =========================
                # CLASS INFO
                # =========================

                class_id = int(
                    box.cls[0]
                )

                class_name = model.names[
                    class_id
                ]

                # =========================
                # TRACK ID
                # =========================

                track_id = int(
                    box.id[0]
                )

                # =========================
                # OBJECT COUNTING
                # =========================

                if track_id not in counted_ids:

                    counted_ids[
                        track_id
                    ] = class_name

                    if class_name not in object_counts:

                        object_counts[
                            class_name
                        ] = 1

                    else:

                        object_counts[
                            class_name
                        ] += 1

                # =========================
                # CUSTOM LABELS
                # =========================

                if track_id not in id_name_map:

                    if class_name not in class_counters:

                        class_counters[
                            class_name
                        ] = 1

                    else:

                        class_counters[
                            class_name
                        ] += 1

                    custom_name = (

                        f"{class_name}"
                        f"{class_counters[class_name]}"

                    )

                    id_name_map[
                        track_id
                    ] = custom_name

                label = id_name_map[
                    track_id
                ]

                # =========================
                # COLOR
                # =========================

                color = class_colors.get(

                    class_name,

                    (255, 255, 255)

                )

                # =========================
                # RECTANGLE
                # =========================

                cv2.rectangle(

                    frame,

                    (x1, y1),

                    (x2, y2),

                    color,

                    2

                )

                # =========================
                # LABEL
                # =========================

                cv2.putText(

                    frame,

                    label,

                    (x1, y1 - 10),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.7,

                    color,

                    2

                )

        # =================================
        # CREATE SIDE PANEL
        # =================================

        panel = np.zeros(

            (height, panel_width, 3),

            dtype=np.uint8

        )

        # =================================
        # PANEL TITLE
        # =================================

        cv2.putText(

            panel,

            "Object Count",

            (20, 40),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            (255, 255, 255),

            2

        )

        # =================================
        # DISPLAY COUNTS
        # =================================

        y_position = 100

        for object_name, count in object_counts.items():

            text_color = class_colors.get(

                object_name,

                (255, 255, 255)

            )

            count_text = (
                f"{object_name}: {count}"
            )

            cv2.putText(

                panel,

                count_text,

                (20, y_position),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                text_color,

                2

            )

            y_position += 45

        # =================================
        # COMBINE VIDEO + PANEL
        # =================================

        combined_frame = cv2.hconcat(
            [frame, panel]
        )

        # =================================
        # SAVE OUTPUT VIDEO
        # =================================

        out.write(
            combined_frame
        )

        # =================================
        # CONVERT FRAME
        # =================================

        ret, buffer = cv2.imencode(
            ".jpg",
            combined_frame
        )

        frame_bytes = buffer.tobytes()

        # =================================
        # STREAM FRAME
        # =================================

        yield (

            b"--frame\r\n"

            b"Content-Type: image/jpeg\r\n\r\n"

            + frame_bytes +

            b"\r\n"

        )

    # =====================================
    # RELEASE
    # =====================================

    cap.release()

    out.release()

    print(
        "Processing Complete!"
    ) 
