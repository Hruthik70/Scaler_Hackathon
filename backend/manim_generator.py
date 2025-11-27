# backend/manim_generator.py
"""
Manim Code Generator
- Objective 2: JSON → Manim object code
- Objective 3: JSON → Manim animation code
- Objective 4: Full Scene code generation + save helper
"""

from typing import Tuple
from pathlib import Path
import uuid

# ---------- Color helpers ----------

def hex_to_manim_color(hex_color: str) -> str:
    """
    Return a color expression that Manim understands.
    Using the hex string directly is valid: color="#FF0000".
    """
    if not isinstance(hex_color, str):
        hex_color = "#FFFFFF"
    hex_color = hex_color.strip()
    if not hex_color.startswith("#"):
        hex_color = "#" + hex_color
    # return as Python string literal in generated code
    return f'"{hex_color}"'


# ---------- Objective 2: object code ----------

def generate_object_code(obj: dict, var_name: str) -> str:
    """
    Generate a single Manim object creation line from JSON.
    """
    obj_type = obj.get("type", "circle").lower()
    color_hex = obj.get("color", "#FFFFFF")
    color_code = hex_to_manim_color(color_hex)

    if obj_type == "circle":
        radius = obj.get("radius", 1)
        code_line = f"{var_name} = Circle(radius={radius}, color={color_code})"

    elif obj_type == "square":
        side = obj.get("side", 1)
        code_line = f"{var_name} = Square(side_length={side}, color={color_code})"

    elif obj_type == "rectangle":
        width = obj.get("width", 2)
        height = obj.get("height", 1)
        code_line = f"{var_name} = Rectangle(width={width}, height={height}, color={color_code})"

    elif obj_type == "text":
        text_content = obj.get("text", "Text")
        font_size = obj.get("font_size", 24)
        # escape double quotes in text to avoid breaking generated code
        safe_text = str(text_content).replace('"', '\\"')
        code_line = f'{var_name} = Text("{safe_text}", color={color_code}, font_size={font_size})'

    else:
        # fallback
        code_line = f"{var_name} = Circle(radius=1, color={color_code})"

    x = obj.get("x", 0)
    y = obj.get("y", 0)
    position_str = f".move_to(np.array([{x}, {y}, 0]))"

    return f"{code_line}{position_str}"


# ---------- Objective 3: animation code ----------

def generate_animation_code(animation: dict, obj_var_map: dict) -> str:
    """
    Generate a single Manim animation line (self.play(...)) from JSON keyframe.
    """
    obj_id = animation.get("object_id")
    anim_type = animation.get("animation_type", animation.get("type", "")).lower()

    # duration: accept ms or seconds
    if "duration_ms" in animation:
        duration_sec = animation["duration_ms"] / 1000.0
    else:
        duration_sec = float(animation.get("duration", 1))

    obj_var = obj_var_map.get(obj_id, "obj_1")
    to_state = animation.get("to_state", {})

    if anim_type == "scale":
        to_radius = to_state.get("radius", animation.get("to", 1))
        anim_code = f"{obj_var}.animate.scale({to_radius})"

    elif anim_type == "move":
        to_x = to_state.get("x", animation.get("to_x", 0))
        to_y = to_state.get("y", animation.get("to_y", 0))
        anim_code = f"{obj_var}.animate.move_to(np.array([{to_x}, {to_y}, 0]))"

    elif anim_type == "rotate":
        angle = to_state.get("angle", animation.get("angle", 0))
        anim_code = f"{obj_var}.animate.rotate({angle})"

    elif anim_type == "fade":
        opacity = to_state.get("opacity", 1.0)
        anim_code = f"FadeOut({obj_var})" if opacity == 0 else f"FadeIn({obj_var})"

    elif anim_type == "color_change":
        to_color = to_state.get("color", animation.get("to_color", "#FFFFFF"))
        color_code = hex_to_manim_color(to_color)
        anim_code = f"{obj_var}.animate.set_color({color_code})"

    else:
        # no-op fallback
        anim_code = f"{obj_var}.animate.scale(1)"

    return f"self.play({anim_code}, run_time={duration_sec})"


# ---------- Objective 4: full scene code ----------

def generate_manim_code(scene_json: dict) -> str:
    """
    Generate complete Manim Scene Python code from scene JSON.

    Expected scene_json format:
    {
      "objects": [...],
      "keyframes": [...],        # or "animations"
      "total_duration_ms": 3000  # or "total_duration" (seconds)
    }
    """
    lines = []
    lines.append("from manim import *")
    lines.append("import numpy as np")
    lines.append("")
    lines.append("class AutoScene(Scene):")
    lines.append("    def construct(self):")

    objects = scene_json.get("objects", [])
    keyframes = scene_json.get("keyframes", scene_json.get("animations", []))

    if "total_duration_ms" in scene_json:
        total_wait = scene_json["total_duration_ms"] / 1000.0
    else:
        total_wait = float(scene_json.get("total_duration", 5))

    # map object_id → obj_1, obj_2, ...
    obj_var_map = {}
    for idx, obj in enumerate(objects, start=1):
        var_name = f"obj_{idx}"
        obj_var_map[obj["id"]] = var_name
        obj_line = generate_object_code(obj, var_name)
        lines.append(f"        {obj_line}")
        lines.append(f"        self.add({var_name})")

    lines.append("")

    # animations
    for anim in keyframes:
        anim_line = generate_animation_code(anim, obj_var_map)
        lines.append(f"        {anim_line}")

    lines.append("")
    lines.append(f"        self.wait({total_wait})")

    return "\n".join(lines)


# ---------- helper: save generated code ----------

def save_scene_code(code_str: str, out_dir: str = "./temp") -> Path:
    fm = FileManager(out_dir)
    file_path = fm.new_scene_path()
    file_path.write_text(code_str, encoding="utf-8")
    return file_path


from datetime import datetime, timedelta

class FileManager:
    """
    Handles directory structure and cleanup for generated scenes and videos.
    """
    def __init__(self, base_dir: str = "./temp"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.scenes_dir = self.base_dir / "scenes"
        self.videos_dir = self.base_dir / "videos"

        self.scenes_dir.mkdir(parents=True, exist_ok=True)
        self.videos_dir.mkdir(parents=True, exist_ok=True)

    def new_scene_path(self) -> Path:
        scene_id = uuid.uuid4().hex[:8]
        return self.scenes_dir / f"scene_{scene_id}.py"

    def move_video(self, src_video: Path) -> Path:
        """
        Move the rendered video from Manim's media folder into ./temp/videos.
        """
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        dest = self.videos_dir / src_video.name
        if src_video.resolve() != dest.resolve():
            dest.write_bytes(src_video.read_bytes())
        return dest.resolve()

    def cleanup_old_files(self, hours_old: int = 2) -> None:
        """
        Delete scene and video files older than given hours.
        """
        cutoff = datetime.now() - timedelta(hours=hours_old)

        for folder in [self.scenes_dir, self.videos_dir]:
            for f in folder.glob("*"):
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime < cutoff:
                        f.unlink()
                except Exception:
                    continue

    def stats(self) -> dict:
        scene_count = len(list(self.scenes_dir.glob("*.py")))
        video_count = len(list(self.videos_dir.glob("*.mp4")))
        total_bytes = 0
        for f in self.base_dir.rglob("*"):
            if f.is_file():
                total_bytes += f.stat().st_size
        return {
            "scene_count": scene_count,
            "video_count": video_count,
            "total_mb": round(total_bytes / (1024 * 1024), 2),
        }


import subprocess
import os

def generate_and_render(scene_json: dict,
                        temp_dir: str = "./temp",
                        quality: str = "pqh") -> str:
    """
    Full pipeline: JSON → Manim .py → MP4 video.

    Returns:
        Absolute path to the rendered MP4 file.
    Raises:
        RuntimeError if rendering fails.
    """
    # 1) Generate Manim Scene code string
    code_str = generate_manim_code(scene_json)

    # 2) Save to temp .py file
    scene_path = save_scene_code(code_str, out_dir=temp_dir)
    scene_path = Path(scene_path).resolve()
    scene_file = scene_path.name  # e.g. scene_ab12cd34.py
    scene_dir = scene_path.parent

    # 3) Build manim command
    # manim -pqh scene_xxx.py AutoScene
    cmd = [
        "manim",
        f"-{quality}",          # e.g. -pqh
        str(scene_file),
        "AutoScene"
    ]

    print("Running:", " ".join(cmd))
    # 4) Run in the directory where the scene file lives
    proc = subprocess.run(
        cmd,
        cwd=str(scene_dir),
        capture_output=True,
        text=True
    )

    if proc.returncode != 0:
        print("STDOUT:\n", proc.stdout)
        print("STDERR:\n", proc.stderr)
        raise RuntimeError("Manim rendering failed")

    # 5) Find the output video
    # Default manim output: <scene_dir>/media/videos/AutoScene/1080p60/AutoScene.mp4
    media_root = scene_dir / "media" / "videos"
    video_file = None

    if media_root.exists():
        for root, _, files in os.walk(media_root):
            for f in files:
                if f.endswith(".mp4"):
                    video_file = Path(root) / f
                    break
            if video_file:
                break

    if not video_file:
        raise RuntimeError("Rendered video file not found in media/videos")

    return str(video_file.resolve())

import subprocess
import os

def generate_and_render(scene_json: dict,
                        temp_dir: str = "./temp",
                        quality: str = "pqh") -> str:
    """
    PUBLIC API for Member 2.
    Called by the Flask backend.

    Input:
        scene_json: dict with keys:
            - "objects": list of objects
            - "keyframes" or "animations": list of animation dicts
            - "total_duration_ms" OR "total_duration"
        temp_dir: base temp folder for scenes/videos.
        quality: manim CLI quality flag, e.g. "pqh" (preview + high).

    Output:
        str: absolute path to the rendered .mp4 video file under temp/videos.

    Raises:
        ValueError: if scene_json is missing required fields.
        RuntimeError: if manim fails or video cannot be found.
    """
    # basic validation
    if not isinstance(scene_json, dict):
        raise ValueError("scene_json must be a dict")
    if "objects" not in scene_json or not scene_json["objects"]:
        raise ValueError("scene_json must contain at least one object")
    if "keyframes" not in scene_json and "animations" not in scene_json:
        raise ValueError("scene_json must contain 'keyframes' or 'animations'")

    fm = FileManager(temp_dir)

    # 1) Generate Scene code
    code_str = generate_manim_code(scene_json)

    # 2) Save to scenes folder
    scene_path = save_scene_code(code_str, out_dir=temp_dir)
    scene_path = Path(scene_path).resolve()
    scene_file = scene_path.name
    scene_dir = scene_path.parent

    # 3) Build and run manim command
    cmd = ["manim", f"-{quality}", scene_file, "AutoScene"]
    print("Running command:", " ".join(cmd))

    proc = subprocess.run(
        cmd,
        cwd=str(scene_dir),
        capture_output=True,
        text=True
    )

    if proc.returncode != 0:
        print("=== MANIM STDOUT ===")
        print(proc.stdout)
        print("=== MANIM STDERR ===")
        print(proc.stderr)
        raise RuntimeError("Manim rendering failed")

    # 4) Locate Manim media video
    media_root = scene_dir / "media" / "videos"
    raw_video = None
    if media_root.exists():
        for root, _, files in os.walk(media_root):
            for f in files:
                if f.endswith(".mp4"):
                    raw_video = Path(root) / f
                    break
            if raw_video:
                break
    if not raw_video:
        raise RuntimeError("Rendered video file not found in media/videos")

    # 5) Move into ./temp/videos and cleanup old files
    final_video = fm.move_video(raw_video)
    fm.cleanup_old_files(hours_old=2)

    return str(final_video)



