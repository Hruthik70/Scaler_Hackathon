from models import SceneModel

def demo():
    sample_scene = {
        "objects": [
            {
                "id": "circle1",
                "type": "circle",
                "x": 0,
                "y": 0,
                "color": "#FF0000",
                "radius": 1.0
            }
        ],
        "animations": [
            {
                "object_id": "circle1",
                "type": "scale",
                "duration": 3.0,
                "from_value": 1.0,
                "to_value": 3.0
            }
        ],
        "total_duration": 5.0
    }

    scene = SceneModel.model_validate(sample_scene)
    print(scene)
    print(scene.model_dump())


if __name__ == "__main__":
    demo()
