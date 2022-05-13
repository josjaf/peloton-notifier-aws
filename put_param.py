import boto3
import json

session = boto3.session.Session()

ssm = session.client('ssm')


def file_to_string(file):
    with open(file, 'r') as myfile:
        file_str = myfile.read()
    myfile.close()

    return file_str


config = file_to_string('config.json')
cfg = json.loads(config)
data = cfg['peloton_credentials']
print(f"Putting Parameter: {cfg['peloton_credentials_parameter_name']} {json.dumps(data)}")
response = ssm.put_parameter(Name=cfg['peloton_credentials_parameter_name'], Value=json.dumps(data), Type='String',
                             Description='Peloton Credentials', Overwrite=True)
print(response)
