import datetime

def update_metrics(current_metrics, new_metric, readings_needed: int):
    if len(current_metrics) >= readings_needed:  # Keep only the last x readings
        current_metrics.pop(0)
    current_metrics.append(new_metric)
    return current_metrics

def extract_metrics(pod_response):
    pod_details = pod_response.json().get('data', {}).get('pod', {})
    try:
        gpu_util = pod_details.get('runtime', {}).get('gpus', [{}])[0].get('gpuUtilPercent', 0)
    except IndexError: # could be a CPU instance with no GPUs
        gpu_util = 0
    cpu_percent = pod_details.get('runtime', {}).get('container', {}).get('cpuPercent', 0)
    memory_percent = pod_details.get('runtime', {}).get('container', {}).get('memoryPercent', 0)

    return {
        'gpu_util': gpu_util,
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'timestamp': datetime.datetime.now().isoformat()
    }

def is_inactive(metrics, readings_needed: int):
    return not is_gpu_active(metrics) and is_cpu_memory_usage_constant(metrics, readings_needed= readings_needed)


def is_gpu_active(metrics):
    gpu_metrics = [metric['gpu_util'] for metric in metrics]
    return any(gpu != 0 for gpu in gpu_metrics)

def is_cpu_memory_usage_constant(metrics, readings_needed: int):
    if len(metrics) < readings_needed:
        return False  # Not enough data to make a decision

    first, last = metrics[0], metrics[-1]
    cpu_change = abs(first['cpu_percent'] - last['cpu_percent'])
    memory_change = abs(first['memory_percent'] - last['memory_percent'])

    cpu_threshold = 5  # Adjust based on expected usage patterns
    memory_threshold = 5  # Adjust similarly

    return cpu_change <= cpu_threshold and memory_change <= memory_threshold
