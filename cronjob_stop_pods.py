import json
import os
import datetime
from src.runpod_budget import runpod
import time

import sys

# Constants for job frequency and stopping criteria in minutes
frequency_cronjob = int(sys.argv[1])  # Frequency of the cron job
inactivity_limit = int(sys.argv[2])  # Inactivity duration before stopping a pod

# Calculate the number of readings needed
READINGS_NEEDED = inactivity_limit // frequency_cronjob


# Placeholder for runpod API client initialization
class RunPodAPI:
    def __init__(self):
        self.runpod = runpod.API()

    def get_pods(self):
        response = self.runpod.get_pods()
        return response

    def get_pod(self, pod_id):
        # Implement API call to fetch a single pod's details
        return self.runpod.get_pod(pod_id)

    def stop_pod(self, pod_id):
        return self.runpod.stop_pod(pod_id)

def load_stats():
    if os.path.exists("pod_stats.json"):
        with open("pod_stats.json", "r") as file:
            return json.load(file)
    return {}

def save_stats(stats):
    with open("pod_stats.json", "w") as file:
        json.dump(stats, file, indent=4)

def update_metrics(current_metrics, new_metric):
    if len(current_metrics) >= READINGS_NEEDED:  # Keep only the last x readings
        current_metrics.pop(0)
    current_metrics.append(new_metric)
    return current_metrics

def is_inactive(metrics):
    # Check if all GPU metrics are 0
    gpu_metrics = [metric['gpu_util'] for metric in metrics]
    if not all(gpu == 0 for gpu in gpu_metrics):
        return False  # GPU was utilized in the last x readings

    # Check if CPU and memory usage have changed
    if len(metrics) < READINGS_NEEDED:
        return False  # Not enough data to make a decision

    # Compare the first and last readings for CPU and memory usage
    first, last = metrics[0], metrics[-1]
    cpu_change = abs(first['cpu_percent'] - last['cpu_percent'])
    memory_change = abs(first['memory_percent'] - last['memory_percent'])

    # Define a threshold for considering if CPU/memory usage has "changed"
    cpu_threshold = 5  # Adjust based on expected usage patterns
    memory_threshold = 5  # Adjust similarly

    # If both CPU and memory usage have not exceeded the threshold, consider it inactive
    if cpu_change <= cpu_threshold and memory_change <= memory_threshold:
        return True
    return False


def check_and_stop_pods(runpod_handler):
    current_stats = load_stats()
    response = runpod_handler.get_pods()
    if response.status_code != 200 or 'errors' in response.json():
        print("Failed to fetch pods")
        return

    pods = response.json().get('data', {}).get('myself', {}).get('pods', [])
    for pod in pods:
        if pod.get('desiredStatus') != 'RUNNING':
            continue

        pod_id = pod['id']
        pod_response = runpod_handler.get_pod(pod_id)
        if pod_response.status_code != 200 or 'errors' in pod_response.json():
            print(f"Failed to fetch pod {pod_id}")
            continue

        pod_details = pod_response.json().get('data', {}).get('pod', {})
        gpu_util = pod_details.get('runtime', {}).get('gpus', [{}])[0].get('gpuUtilPercent', 0)
        cpu_percent = pod_details.get('runtime', {}).get('container', {}).get('cpuPercent', 0)
        memory_percent = pod_details.get('runtime', {}).get('container', {}).get('memoryPercent', 0)

        new_metric = {
            'gpu_util': gpu_util,
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'timestamp': datetime.datetime.now().isoformat()
        }

        if pod_id not in current_stats:
            current_stats[pod_id] = {'metrics': []}

        current_stats[pod_id]['metrics'] = update_metrics(current_stats[pod_id].get('metrics', []), new_metric)

        if is_inactive(current_stats[pod_id]['metrics']):
            print(f"Stopping pod {pod_id} due to inactivity.")
            stop_response = runpod_handler.stop_pod(pod_id)
            if stop_response.status_code == 200:
                print(f"Pod {pod_id} stopped successfully.")
                del current_stats[pod_id]  # Remove stats for stopped pods
            else:
                print(f"Failed to stop pod {pod_id}.")
        else:
            print(f"Pod {pod_id} remains active with current GPU utilization at {gpu_util}%.")

    save_stats(current_stats)

if __name__ == "__main__":
    runpod_object = RunPodAPI()
    print("Starting the cron job to stop inactive pods...")
    while True:
        check_and_stop_pods(runpod_object)
        # Convert X_MINUTES to seconds for sleep interval
        time.sleep(frequency_cronjob * 60)
