from constructs import Construct
from aws_cdk import App, Stack                    # core constructs
from aws_cdk import (
    Environment,
    App,
    aws_logs,
)
import os
import pathlib
import json


def file_to_string(file):
    with open(file, 'r') as myfile:
        file_str = myfile.read()
    myfile.close()

    return file_str


config = file_to_string('config.json')
cfg = json.loads(config)
env_pipeline = Environment(account=cfg['pipeline_account']['id'], region=cfg['pipeline_account']['region'])
from PelotonNotifier import PelotonNotifier
from Pipeline import PipelineS

env = Environment(account=cfg['account'], region=os.environ['CDK_DEFAULT_REGION'])
app = App()
PelotonNotifier(app, "PelotonNotifier", env=env, description='Peloton Notifier')

app.synth()
