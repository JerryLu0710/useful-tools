"""Core logic for image tools."""

import os
import sys

import cv2

from logger_setup import get_logger

logger = get_logger(__name__, "image_tool")


def mark_coordinates(image_path, resize_ratio=None):
    """
    Image Viewer and Coordinate Marker
    """
    image = cv2.imread(image_path)
    if image is None:
        logger.error("Unable to load image.")
        sys.exit(1)

    display_image = image.copy()

    if resize_ratio:
        height, width = image.shape[:2]
        new_width = int(width * resize_ratio)
        new_height = int(height * resize_ratio)
        display_image = cv2.resize(image, (new_width, new_height))

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if resize_ratio:
                orig_x = int(x / resize_ratio)
                orig_y = int(y / resize_ratio)
            else:
                orig_x, orig_y = x, y

            cv2.circle(display_image, (x, y), 5, (0, 0, 255), -1)
            cv2.putText(
                display_image,
                f"({orig_x}, {orig_y})",
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
            cv2.imshow("Image", display_image)

    cv2.imshow("Image", display_image)
    cv2.setMouseCallback("Image", click_event)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            save_path = f"{base_name}_marked.jpg"
            cv2.imwrite(save_path, display_image)
            logger.info(f"Image saved as {save_path}")
        elif key == ord("q"):
            break

    cv2.destroyAllWindows()


def extract_frame(video_path, desired_time, output_dir):
    """
    Video Frame Extractor
    """
    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        raise OSError(f"Error: Could not open video {video_path}")

    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_number = int(fps * desired_time)

    if frame_number >= total_frames:
        raise ValueError(f"Error: The video is shorter than {desired_time} seconds.")

    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    ret, frame = video.read()
    if not ret:
        raise OSError(f"Error: Could not read frame at {desired_time} seconds.")

    output_image_path = os.path.join(output_dir, f"frame_at_{desired_time}s.jpg")
    cv2.imwrite(output_image_path, frame)

    video.release()

    return output_image_path


def capture_and_save_images(camera_index, save_dir):
    """
    Camera Capture and Image Saver
    """
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        raise OSError(f"Error: Could not open camera {camera_index}.")

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    img_counter = 1

    logger.info("Press 's' to save an image, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("Can't receive frame. Exiting ...")
            break

        cv2.imshow("Camera", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            img_name = os.path.join(save_dir, f"{img_counter:02d}.jpg")
            cv2.imwrite(img_name, frame)
            logger.info(f"{img_name} saved!")
            img_counter += 1
        elif key == ord("q"):
            logger.info("Quitting...")
            break

    cap.release()
    cv2.destroyAllWindows()
