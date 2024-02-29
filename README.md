# RunPod-Budget

This repository is purely built from Ashley Kleynhans's collection of Python scripts for calling the RunPod GraphQL API [runpod-api](https://github.com/ashleykleynhans/runpod-api). This repo will be here until the original repo is updated with the latest changes. All credits to him. I am just adding a cron job here.

## Getting started


### Clone the repo, create venv and install dependencies

```bash
git clone git@github.com:gitlost-murali/runpod-budget.git
cd runpod-api
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Configure your RunPod API

Copy the `.env.example` file to `.env` as follows:


```bash
cp .env.example .env
```

Then edit the `.env` file and replace the text `INSERT_YOUR_RUNPOD_API_KEY_HERE`
with your RunPod API key that you can get from the [RunPod Settings](
https://www.runpod.io/console/user/settings) in the RunPod Web console.

`python cronjob_stop_pods.py 10 120` runs the script every 10 minutes and stops the pods that are running for more than 120 minutes with zero GPU utlization.