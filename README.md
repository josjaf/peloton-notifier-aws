# Guide
* This package is an AWS CDK Application that will send you a notification every week with the amount of minutes you spend with each Peloton Cycling Instructor
* Emails are sent once a week by AWS SNS
### Prereqs
* AWS Account
* Peloton Account
* SSM Parameter with Peloton Credentials
* Docker and AWS CDK installed and running on your Machine
#### Libaries
* (Peloton SDK)[https://github.com/geudrik/peloton-client-library]
* (AWS CDK)[https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html]

#### Peloton Credentials
* Take the `config-sample.json` and add your values, rename to `config.json`
* Upload SSM Paramter for Credentials
* `cp config-sample.json config.json`
* Replace `config.json` values
  * emails, peloton credentials
* Run `put_param.py` to add the parameter to your account

#### Setup
* Docker must be installed and running - it is required for building the Lambda Layer and Zip since the package you are creating for Lambda is probably not the same system architecture you are currently using
  * MacOS needs Docker to build numpy and pandas for the Lambda runtime
* Run `cdk deploy "*" --require-approval never -vll` from the git root
* You can run a test event with Lambda, the function does not require any specific input in the invoking event