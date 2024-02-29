from src.runpod_budget import runpod
import time
import sys
from src.runpod_budget.cronjob_utils.metrics import update_metrics, extract_metrics, is_inactive, update_metrics
from src.runpod_budget.cronjob_utils.stats import load_stats, save_stats
from src.runpod_budget.cronjob_utils.runpod_handler import RunPodAPI

# Constants for job frequency and stopping criteria in minutes
frequency_cronjob = int(sys.argv[1])  # Frequency of the cron job
inactivity_limit = int(sys.argv[2])  # Inactivity duration before stopping a pod

# Calculate the number of readings needed
READINGS_NEEDED = inactivity_limit // frequency_cronjob

def check_and_stop_pods(runpod_handler):
    current_stats = load_stats()
    response = runpod_handler.get_pods()
    if response.status_code != 200: # or 'errors' in response.json():
        print("Failed to fetch pods")
        return

    pods = response.json().get('data', {}).get('myself', {}).get('pods', [])
    for pod in pods:
        if pod.get('desiredStatus') != 'RUNNING':
            continue

        process_pod(pod, current_stats, runpod_handler)

    save_stats(current_stats)

def process_pod(pod, current_stats, runpod_handler):
    pod_id = pod['id']
    pod_response = runpod_handler.get_pod(pod_id)

    if pod_response.status_code != 200: # or 'errors' in pod_response.json():
        print(f"Failed to fetch pod {pod_id}")
        return

    try:
        new_metric = extract_metrics(pod_response)
    except Exception as e:
        print(f"Failed to fetch metrics for pod {pod_id}: {e}")
        return

    if pod_id not in current_stats:
        current_stats[pod_id] = {'metrics': []}

    current_stats[pod_id]['metrics'] = update_metrics(current_stats[pod_id].get('metrics', []), new_metric, readings_needed=READINGS_NEEDED)

    if is_inactive(current_stats[pod_id]['metrics'], READINGS_NEEDED):
        stop_pod(pod_id, current_stats, runpod_handler)
    else:
        print(f"Pod {pod_id} remains active with current GPU utilization at {new_metric['gpu_util']}%.")


def stop_pod(pod_id, current_stats, runpod_handler):
    print(f"Stopping pod {pod_id} due to inactivity.")
    stop_response = runpod_handler.stop_pod(pod_id)
    if stop_response.status_code == 200:
        print(f"Pod {pod_id} stopped successfully.")
        del current_stats[pod_id]  # Remove stats for stopped pods
    else:
        print(f"Failed to stop pod {pod_id}.")

if __name__ == "__main__":
    runpod_object = RunPodAPI(runpod.API())
    print("Starting the cron job to stop inactive pods...")
    while True:
        check_and_stop_pods(runpod_object)
        time.sleep(frequency_cronjob * 60)