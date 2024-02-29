
class RunPodAPI:
    def __init__(self, runpod_api):
        self.runpod = runpod_api

    def get_pods(self):
        return self.runpod.get_pods()

    def get_pod(self, pod_id):
        return self.runpod.get_pod(pod_id)

    def stop_pod(self, pod_id):
        return self.runpod.stop_pod(pod_id)
