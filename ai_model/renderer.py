# backend/renderer.py
from typing import Dict, Any, List
from PIL import Image, ImageDraw, ImageFont


class FrameRenderer:
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self.bg_color = (15, 15, 20)

    @staticmethod
    def _hex_to_rgb(code: str):
        code = code.lstrip("#")
        if len(code) != 6:
            return (255, 255, 255)
        r = int(code[0:2], 16)
        g = int(code[2:4], 16)
        b = int(code[4:6], 16)
        return (r, g, b)

    def render_frame(self, objects_state: Dict[str, Any]) -> Image.Image:
        img = Image.new("RGB", (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)

        for obj in objects_state.values():
            otype = obj.get("type")
            color = self._hex_to_rgb(obj.get("color", "#FFFFFF"))
            x = float(obj.get("x", self.width / 2))
            y = float(obj.get("y", self.height / 2))

            if otype == "circle":
                r = float(obj.get("radius", 50))
                bbox = [x - r, y - r, x + r, y + r]
                draw.ellipse(bbox, fill=color)

            elif otype == "rectangle":
                w = float(obj.get("width", 100))
                h = float(obj.get("height", 50))
                bbox = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
                draw.rectangle(bbox, fill=color)

            elif otype == "text":
                text = str(obj.get("text", "Text"))
                font_size = int(obj.get("font_size", 32))
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except Exception:
                    font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), text, font=font)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
                draw.text((x - tw / 2, y - th / 2), text, fill=color, font=font)

        return img

    def render_all_frames(self, frame_states: List[Dict[str, Any]]) -> List[Image.Image]:
        return [self.render_frame(state) for state in frame_states]
