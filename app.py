from aws_cdk import (
    aws_events as events,
    aws_lambda as lambda_,
    aws_lambda_destinations,
    aws_sns,
    aws_ssm,
    aws_iam,
    aws_s3,
    aws_sns_subscriptions,
    aws_events_targets as targets,
    core,
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
env_pipeline = core.Environment(account=cfg['pipeline_account']['id'], region=cfg['pipeline_account']['region'])
from PelotonNotifier import PelotonNotifier
from Pipeline import PipelineS
env = core.Environment(account=os.environ['CDK_DEFAULT_ACCOUNT'], region=os.environ['CDK_DEFAULT_REGION'])
app = core.App()
PelotonNotifier(app, "PelotonNotifier", env=env, description='Peloton Notifier')


app.synth()
