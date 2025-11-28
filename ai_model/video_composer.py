# backend/video_composer.py
from typing import List
from PIL import Image
import cv2
import numpy as np


class VideoComposer:
    @staticmethod
    def compose_frames_to_mp4(frames: List[Image.Image], output_path: str, fps: int = 30):
        if not frames:
            raise ValueError("No frames to compose")

        w, h = frames[0].size
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        for img in frames:
            if img.size != (w, h):
                img = img.resize((w, h))
            frame_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            writer.write(frame_bgr)

        writer.release()
