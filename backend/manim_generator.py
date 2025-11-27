from typing import Tuple

def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
    """
    Convert hex color #RRGGBB to RGB tuple (0-1 range for Manim).
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        print(f"Warning: Invalid hex color '{hex_color}', defaulting to white")
        return (1.0, 1.0, 1.0)
    try:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)
    except ValueError:
        print(f"Warning: Error parsing hex color '{hex_color}', defaulting to white")
        return (1.0, 1.0, 1.0)

def hex_to_manim_color(hex_color: str) -> str:
    """
    Convert hex color to Manim RGBColor string.
    """
    r, g, b = hex_to_rgb(hex_color)
    return f"RGBColor({r:.3f},{g:.3f},{b:.3f})"

# Supported object classes
OBJECT_TYPE_MAPPING = {
    "circle": "Circle",
    "square": "Square",
    "rectangle": "Rectangle",
    "text": "Text"
}

# Parameters per object type
OBJECT_PARAMETERS = {
    "circle": ["radius", "color"],
    "square": ["side", "color"],
    "rectangle": ["width", "height", "color"],
    "text": ["text", "color", "font_size"]
}


def generate_object_code(obj: dict, var_name: str) -> str:
    """
    Convert JSON object to Manim object creation code line.
    """
    obj_type = obj.get("type", "circle").lower()

    # Convert color
    color_hex = obj.get("color", "#FFFFFF")
    color_code = hex_to_manim_color(color_hex)

    # Handle based on type
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
        code_line = f'{var_name} = Text("{text_content}", color={color_code}, font_size={font_size})'

    else:
        # Default fallback
        code_line = f"{var_name} = Circle(radius=1, color={color_code})"

    # Add position
    x = obj.get("x", 0)
    y = obj.get("y", 0)
    position_str = f".move_to(np.array([{x}, {y}, 0]))"

    # Final full line
    full_line = f"{code_line}{position_str}"
    return full_line


def generate_animation_code(animation: dict, obj_var_map: dict) -> str:
    """
    Convert JSON animation keyframe description to Manim animation code line.

    Args:
        animation (dict): Animation keyframe with keys:
            - object_id (str): ID of the object to animate
            - animation_type (str): Type (e.g., "scale", "move", "rotate", "fade", "color_change")
            - start_time_ms (int): Start time in milliseconds (ignored here)
            - duration_ms (int): Duration in milliseconds (converted to seconds)
            - from_state (dict): State before animation
            - to_state (dict): State after animation

        obj_var_map (dict): Map from object_id to variable names in Manim code (e.g., "obj_1")

    Returns:
        str: A string with Manim animation code, e.g., "self.play(obj_1.animate.scale(3), run_time=2)"
    """
    obj_id = animation.get("object_id")
    anim_type = animation.get("animation_type", "").lower()
    duration_ms = animation.get("duration_ms", 1000)
    duration_sec = duration_ms / 1000.0

    # Map object_id to variable name
    obj_var = obj_var_map.get(obj_id, "obj_1")

    from_state = animation.get("from_state", {})
    to_state = animation.get("to_state", {})

    # Generate animation code based on animation_type
    if anim_type == "scale":
        to_radius = to_state.get("radius") or to_state.get("scale") or 1
        anim_code = f"{obj_var}.animate.scale({to_radius})"

    elif anim_type == "move":
        to_x = to_state.get("x", 0)
        to_y = to_state.get("y", 0)
        anim_code = f"{obj_var}.animate.move_to(np.array([{to_x}, {to_y}, 0]))"

    elif anim_type == "rotate":
        # Angle in radians or degrees? Assuming radians here
        angle = to_state.get("angle", 0)
        anim_code = f"{obj_var}.animate.rotate({angle})"

    elif anim_type == "fade":
        # Fade in or out based on opacity in to_state
        opacity = to_state.get("opacity", 1.0)
        if opacity == 0:
            anim_code = f"FadeOut({obj_var})"
        else:
            anim_code = f"FadeIn({obj_var})"

    elif anim_type == "color_change":
        to_color = to_state.get("color", "#FFFFFF")
        color_code = hex_to_manim_color(to_color)
        anim_code = f"{obj_var}.animate.set_color({color_code})"

    else:
        # Default fallback animation (no-op scale)
        anim_code = f"{obj_var}.animate.scale(1)"

    # Wrap with self.play and duration
    play_code = f"self.play({anim_code}, run_time={duration_sec})"
    return play_code

