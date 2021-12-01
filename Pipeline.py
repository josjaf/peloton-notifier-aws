from aws_cdk import (
    aws_s3,
    core,
    aws_codecommit,
)
from aws_cdk.core import Environment
from aws_cdk.pipelines import (
    CodePipeline,
    ShellStep,
    CodePipelineSource
)

from PelotonNotifier import PelotonNotifier
import os




class PipelineS(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs) -> None:
        super().__init__(app, id)
        # bucket = aws_s3.Bucket(self, 'Bucket', versioned=True)
        repo = aws_codecommit.Repository(self, 'Repo', repository_name='pipeline-mirror')
        #env = core.Environment(account=os.environ['CDK_DEFAULT_ACCOUNT'], region=os.environ['CDK_DEFAULT_REGION'])

        pipeline = CodePipeline(self, "Pipeline",
                                synth=ShellStep("Synth",
                                                # Use a connection created using the AWS console to authenticate to GitHub
                                                # Other sources are available.
                                                # input=CodePipelineSource.s3(bucket=bucket, object_key="repo.zip",
                                                #                             action_name="GitZip"
                                                #                             ),
                                                input=CodePipelineSource.code_commit(repository=repo, branch="dev",
                                                                            ),
                                                commands=["npm ci", "npm run build", "npx cdk synth"
                                                          ]
                                                )
                                )

        # 'MyApplication' is defined below. Call `addStage` as many times as
        # necessary with any account and region (may be different from the
        # pipeline's).
        pipeline.add_stage(MyApplication(self, "Prod",
                                         # env=Environment(
                                         #     account="12345",
                                         #     region="us-east-1"
                                         # )
                                         ))
class MyApplication(core.Stage):
    def __init__(self, scope, id, *, env=None, outdir=None):
        super().__init__(scope, id, env=env, outdir=outdir)
        app = core.App()
        MainStack = PelotonNotifier(self, "PelotonNotify2")