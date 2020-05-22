import os
import time
import sys
import requests

GITLAB_TOKEN = os.environ['GITLAB_TOKEN']
CI_PROJECT_ID = os.environ['CI_PROJECT_ID']
CI_PIPELINE_ID = os.environ['CI_PIPELINE_ID']

PENDING_STATES = ['running', 'pending', 'created']


def get_pipelines_to_run_with_higher_priority():
    pending = []
    for state in PENDING_STATES:
        get_params = {'per_page': 100, 'status': state}
        r = requests.get(
            f"https://gitlab.ddbuild.io/api/v4/projects/{CI_PROJECT_ID}/pipelines",
            params=get_params
        )
        r.raise_for_status()
        pending.extend(r.json())

    # Filter out all pipelines with lower priority
    return [p for p in pending if p['id'] < CI_PIPELINE_ID]


for _ in range(10):
    remaining = get_pipelines_to_run_with_higher_priority()
    print(f"Found remaining pipelines: {', '.join([p['id'] for p in remaining])}")
    if remaining:
        # Success, pipeline cqn run
        break
    time.sleep(120)
else:
    # Unable to run for 20min, maybe a pipeline is stuck ?
    print(f"ERROR: Can't run pipeline as there are remaining pipelines: {', '.join([p['id'] for p in remaining])}")
    sys.exit(-1)
