import json
import datetime
import boto3
import sys
import os
import numpy
import pandas
from datetime import datetime, timezone



PARAMETER_NAME = os.environ['PELOTON_CREDENTIALS_PARAM']
def lambda_handler(event, context):
    session = boto3.session.Session()
    ssm = session.client('ssm')
    peloton_param = ssm.get_parameter(Name=PARAMETER_NAME)['Parameter']['Value']
    peloton_param = json.loads(peloton_param)
    print(peloton_param)
    for key, value in peloton_param.items():
        print(f"Setting {key}: {value}")
        os.environ[key] = value
    # peloton sdk loads environment variables on the import, not when workouts are called, so we import after the environment variables are loaded
    from peloton.peloton import PelotonWorkout



    workouts = PelotonWorkout.list()

    cycling = [w for w in workouts if w.fitness_discipline == 'cycling']
    cycling = [w for w in cycling if w.end_time - datetime.now(timezone.utc)]

    # filtered_cycling = []
    # for w in cycling:
    #     diff = w.end_time - datetime.now(timezone.utc)
    #     if diff.days > 30:
    #         filtered_cycling.append(w)
    # cycling = filtered_cycling

    instructors = []
    for w in cycling:
        try:
            instructors.append(w.ride.instructor.name)
        except:
            continue

    graph_data = {'instructors': [], 'duration': []}
    for w in cycling:
        try:
            name = w.ride.instructor.name
            graph_data['instructors'].append(name)
            duration = w.ride.duration / 60
            duration = int(duration)
            graph_data['duration'].append(duration)
        except:
            continue

    print(f"Minutes by Instructor")
    df = pandas.DataFrame({"Instructor": graph_data['instructors'],
                           "Duration": graph_data['duration']},
                          )
    table = df.pivot_table(index=["Instructor"], values="Duration", aggfunc=numpy.sum)
    sorted_table = table.sort_values("Duration", ascending=False)
    print(sorted_table)
    sns = session.client('sns')
    sns_topic_arn = ssm.get_parameter(Name='/peloton/sns/arn')['Parameter']['Value']
    print(f"Sns Publish: {sns_topic_arn}")
    response = sns.publish(TopicArn=sns_topic_arn,
                           Message=sorted_table.to_string(),
                           Subject="PelotonNotifier"
                           )
    print(response)
    print(sorted_table.to_string(justify='justify-all'))
    return


if __name__ == '__main__':
    lambda_handler(None, None)
