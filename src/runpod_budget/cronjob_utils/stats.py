import json
import os

def load_stats():
    if os.path.exists("pod_stats.json"):
        with open("pod_stats.json", "r") as file:
            return json.load(file)
    return {}

def save_stats(stats):
    with open("pod_stats.json", "w") as file:
        json.dump(stats, file, indent=4)
