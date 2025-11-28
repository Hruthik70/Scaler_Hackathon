# backend/app.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
from educational_generator import generate_educational_manim
import subprocess
import tempfile
import shutil
import uuid

from models import Scene
from parser_groq import parse_with_groq
from animator import AnimationEngine
from renderer import FrameRenderer
from video_composer import VideoComposer

load_dotenv()

app = Flask(__name__)
CORS(app)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200


@app.route('/generate/render-educational', methods=['POST'])
def render_educational():
    """Full pipeline: text → Manim code → rendered video"""
    try:
        data = request.get_json() or {}
        description = data.get("description", "").strip()

        if not description:
            return jsonify({"error": "Description required"}), 400

        # Step 1: Generate Manim code
        manim_code = generate_educational_manim(description)

        # Step 2: Save to temporary file
        temp_dir = tempfile.mkdtemp()
        scene_file = os.path.join(temp_dir, "generated_scene.py")

        with open(scene_file, 'w', encoding='utf-8') as f:
            f.write(manim_code)

        # Step 3: Run Manim
        result = subprocess.run(
            ['manim', '-pql', scene_file, 'EducationalScene'],
            capture_output=True,
            text=True,
            cwd=temp_dir
        )

        if result.returncode != 0:
            return jsonify({
                "error": "Manim compilation failed",
                "stderr": result.stderr,
                "code": manim_code
            }), 500

        # Step 4: Find the output video
        media_dir = os.path.join(temp_dir, "media", "videos", "generated_scene", "480p15")
        video_files = [f for f in os.listdir(media_dir) if f.endswith('.mp4')]

        if not video_files:
            return jsonify({"error": "Video file not found"}), 500

        # Step 5: Copy video to outputs folder
        video_id = str(uuid.uuid4())[:8]
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        final_video_path = os.path.join(output_dir, f"{video_id}.mp4")

        shutil.copy(
            os.path.join(media_dir, video_files[0]),
            final_video_path
        )

        # Cleanup temp directory
        shutil.rmtree(temp_dir)

        return jsonify({
            "video_id": video_id,
            "video_url": f"/outputs/{video_id}.mp4",
            "manim_code": manim_code,
            "message": "Video rendered successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/generate/scenes', methods=['POST'])
def generate_scenes():
    """Uses Groq to convert text description to Scene JSON."""
    try:
        data = request.get_json() or {}
        description = (data.get("description") or "").strip()
        if not description:
            return jsonify({"error": "Description required"}), 400

        scene = parse_with_groq(description)
        return jsonify(scene.model_dump()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/render', methods=['POST'])
def render():
    """Renders a Scene JSON into an MP4 video."""
    try:
        scene_data = request.get_json() or {}
        scene = Scene(**scene_data)

        # 1) Generate frame states
        animator = AnimationEngine(scene)
        frame_states = animator.generate_all_frame_states(fps=30)

        # 2) Render frames
        renderer = FrameRenderer(scene.canvas_width, scene.canvas_height)
        frames = renderer.render_all_frames(frame_states)

        # 3) Compose video
        video_id = str(uuid.uuid4())[:8]
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        video_path = os.path.join(output_dir, f"{video_id}.mp4")

        VideoComposer.compose_frames_to_mp4(frames, video_path, fps=30)

        return jsonify({
            "video_id": video_id,
            "video_url": f"/outputs/{video_id}.mp4",
            "frame_count": len(frames),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/outputs/<filename>', methods=['GET'])
def serve_video(filename):
    video_path = os.path.join("outputs", filename)
    if os.path.exists(video_path):
        return send_file(video_path, mimetype="video/mp4")
    return jsonify({"error": "Video not found"}), 404


@app.route('/generate/educational', methods=['POST'])
def generate_educational():
    """For educational/math animations, generate Manim code directly"""
    try:
        data = request.get_json() or {}
        description = data.get("description", "").strip()

        if not description:
            return jsonify({"error": "Description required"}), 400

        manim_code = generate_educational_manim(description)

        return jsonify({
            "manim_code": manim_code,
            "type": "educational"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
