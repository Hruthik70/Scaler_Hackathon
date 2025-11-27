from datasets import Dataset
import json

# Your training data - 20 examples to start (expand to 100+ later)
TRAINING_DATA = [
    {
        "input_text": "a red circle grows from radius 1 to 3 in 3 seconds",
        "target_json": '{"objects":[{"id":"circle1","type":"circle","x":0,"y":0,"color":"#FF0000","radius":1}],"animations":[{"object_id":"circle1","type":"scale","duration":3,"to_value":3}],"total_duration":5}'
    },
    {
        "input_text": "blue square moves right 4 units in 2 seconds",
        "target_json": '{"objects":[{"id":"square1","type":"square","x":0,"y":0,"color":"#0000FF","side":1}],"animations":[{"object_id":"square1","type":"move","duration":2,"to_x":4,"to_y":0}],"total_duration":5}'
    },
    {
        "input_text": "green circle fades in over 1 second then scales up",
        "target_json": '{"objects":[{"id":"circle1","type":"circle","x":0,"y":0,"color":"#00FF00","radius":1}],"animations":[{"object_id":"circle1","type":"fadein","duration":1},{"object_id":"circle1","type":"scale","duration":2,"to_value":2}],"total_duration":5}'
    },
    # Add 17 more examples covering different combinations...
]


def create_dataset():
    data = []
    for item in TRAINING_DATA:
        data.append({
            "input_text": f"generate scene: {item['input_text']}",
            "target_text": item['target_json']
        })

    return Dataset.from_list(data)

if __name__ == "__main__":
    dataset = create_dataset()
    dataset.to_json("dataset.json")
    print(f"✅ Saved {len(dataset)} examples to dataset.json")
