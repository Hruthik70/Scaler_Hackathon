# backend/animator.py
from typing import List, Dict, Any
from models import Scene


class AnimationEngine:
    def __init__(self, scene: Scene):
        self.scene = scene

    @staticmethod
    def lerp(start: float, end: float, t: float) -> float:
        return start + (end - start) * t

    def generate_all_frame_states(self, fps: int = 30) -> List[Dict[str, Any]]:
        total_frames = int(self.scene.total_duration_ms * fps / 1000)
        objects = {obj.id: obj.model_copy().dict() for obj in self.scene.objects}
        active_keyframes = self.scene.keyframes

        frame_states: List[Dict[str, Any]] = []

        for frame_idx in range(total_frames):
            t_ms = frame_idx * 1000 / fps
            current_objects = {oid: data.copy() for oid, data in objects.items()}

            for kf in active_keyframes:
                start = kf.start_time_ms
                end = kf.start_time_ms + kf.duration_ms
                if not (start <= t_ms <= end):
                    continue

                progress = (t_ms - start) / kf.duration_ms
                progress = max(0.0, min(1.0, progress))

                obj_state = current_objects.get(kf.object_id)
                if not obj_state:
                    continue

                for key, start_val in kf.from_state.items():
                    end_val = kf.to_state.get(key, start_val)
                    if isinstance(start_val, (int, float)) and isinstance(end_val, (int, float)):
                        obj_state[key] = self.lerp(float(start_val), float(end_val), progress)
                    else:
                        obj_state[key] = end_val if progress >= 1.0 else start_val

            frame_states.append(current_objects)

        return frame_states
