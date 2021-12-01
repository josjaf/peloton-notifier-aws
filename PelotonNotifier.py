from aws_cdk import (
    aws_events as events,
    aws_lambda as lambda_,
    aws_sns,
    aws_ssm,
    aws_iam,
    aws_sns_subscriptions,
    aws_events_targets as targets,
    core,
    aws_logs,
    aws_lambda_python

)
from pathlib import Path
import json

def file_to_string(file):
    with open(file, 'r') as myfile:
        file_str = myfile.read()
    myfile.close()

    return file_str
config = file_to_string('config.json')
cfg = json.loads(config)
class PelotonNotifier(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id)

        sns_topic = aws_sns.Topic(
            self, "Topic"
        )
        for i in cfg['emails']:
            sns_topic.add_subscription(subscription=aws_sns_subscriptions.EmailSubscription(i))
        layer_path = Path.joinpath(Path.cwd(), 'layer/')
        bundle = core.BundlingOptions(
            image=lambda_.Runtime.PYTHON_3_8.bundling_image,
            working_directory=str(layer_path),
            command=[
                "bash", "-c",
                # "ls -lha /asset-input/",
                # "cat -lha /asset-input/requirements.txt",
                # # "pip install --no-cache -r /app/requirements.txt -t /asset-output && cp -au . /asset-output"
                # "mkdir /asset-output",
                # "touch /asset-output/test.txt"
                "ls -lha && echo josh && pip install --no-cache -r /asset-input/requirements.txt -t /asset-output/python && git clone https://github.com/geudrik/peloton-client-library.git /asset-output/python/peloton"

            ],
        )

        main_layer = lambda_.LayerVersion(
            self, "mainlayer",
            code=lambda_.Code.from_asset('layer', bundling=bundle),
            removal_policy=core.RemovalPolicy.RETAIN,
            compatible_architectures=[lambda_.Architecture.X86_64],
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
        )
        # main_layer = aws_lambda_python.PythonLayerVersion(
        #     self, "mainlayer",
        #     entry=str(layer_path),
        #
        #     compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
        # )
        lambda_function = lambda_.Function(
            self, "PelotonNotifier",
            code=lambda_.AssetCode('./function/'),
            handler="lambda_function.lambda_handler",
            timeout=core.Duration.seconds(30),
            runtime=lambda_.Runtime.PYTHON_3_8,
            log_retention=aws_logs.RetentionDays.ONE_MONTH,
            retry_attempts=1,
            # on_failure=aws_lambda_destinations.SnsDestination(sns_topic),
            layers=[main_layer],
            environment={
                'PELOTON_CREDENTIALS_PARAM': cfg['peloton_credentials_parameter_name']
            }
        )
        parameter = aws_ssm.StringParameter.from_string_parameter_name(self, 'apiparam',
                                                                       string_parameter_name=cfg['peloton_credentials_parameter_name'])
        parameter.grant_read(lambda_function)
        lambda_function.role.add_to_policy(aws_iam.PolicyStatement(
            sid="Parameters",
            effect=aws_iam.Effect.ALLOW,
            actions=['ssm:GetParameter', 'ssm:GetParameters',
                     'ssm:GetParameterHistory'],
            resources=[
                f"arn:aws:ssm:{core.Aws.REGION}:{core.Aws.ACCOUNT_ID}:parameter/peloton*",
                f"arn:aws:ssm:{core.Aws.REGION}:{core.Aws.ACCOUNT_ID}:parameter/peloton/json",
                "*"]
        ))
        sns_topic.grant_publish(lambda_function)
        version_parameter = aws_ssm.StringParameter(
            self, "SNSTopic",
            parameter_name="/peloton/sns/arn",
            string_value=sns_topic.topic_arn,
            description='SNS Topic Arn'
        )

        dev_version = lambda_.Version(
            self, "devversion2",
            lambda_=lambda_function,
            # code_sha256=
        )

        dev_alias = lambda_.Alias(
            self, "devalias",
            alias_name='dev',
            version=dev_version

        )
        prod_alias = lambda_.Alias(
            self, "prodalias",
            alias_name='prod',
            version=dev_version

        )

        #
        # # api_param.grant_read(lambda_function)
        #
        # # Run every day at 6PM UTC
        # # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.cron(
                day='*/14',
                minute='15',
                hour='23',
                month='*',
                year='*'),
        )
        # rule.add_target(targets.LambdaFunction(prod_alias))
        rule.add_target(targets.LambdaFunction(lambda_function))
        for i in [lambda_function, rule]:
            core.Tags.of(i).add('Name', 'PelotonNotifier')
            core.Tags.of(i).add('App', 'PelotonNotifier')
