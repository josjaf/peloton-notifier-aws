import json
import datetime
import boto3
import sys
import os
import numpy
import pandas
from datetime import datetime, timezone
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


PARAMETER_NAME = os.environ['PELOTON_CREDENTIALS_PARAM']
def lambda_handler(event, context):
    session = boto3.session.Session()
    ssm = session.client('ssm')
    peloton_param = ssm.get_parameter(Name=PARAMETER_NAME)['Parameter']['Value']
    peloton_param = json.loads(peloton_param)
    print(peloton_param)
    for key, value in peloton_param.items():
        if key.startswith('PELOTON'):
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
    data = {}

    # instructors = []
    # for w in cycling:
    #     try:
    #         instructors.append(w.ride.instructor.name)
    #     except:
    #         continue
    #
    # instructors = set(instructors)
    # for i in instructors:
    #     data[i] = 0
    cycling = [i for i in cycling if hasattr(i.ride, 'instructor')]
    for w in cycling:
        try:

            name = w.ride.instructor.name
            # check if the key already exists in the dictionary, and if it doesn't, add it and set to 0
            if name not in data:
                data[name] = 0
            duration = w.ride.duration / 60
            duration = int(duration)
            data[name] += duration
        except Exception as e:
            print(e)
            continue


    result = {key: val for key, val in data.items() if val >= 60}
    graph_data = {'instructors': result.keys(), 'duration': result.values()}
    message = ""
    #WantedOutput = sorted(MyDict, key=lambda x : MyDict[x])
    out = sorted(result.items(), key=lambda x: x[1], reverse=True)
    string_length = 20
    title = "Instructor"
    difference = string_length - len(title)
    title_string = f'{title}{difference * " "}Minutes\n'
    main_string = title_string
    for i in out:
        name = i[0]
        mins = i[1]
        difference = string_length - len(name)
        new_string = f'{name}{difference * " "}'
        main_string = main_string + f"{new_string}{mins}\n"
    print(main_string)
    df = pandas.DataFrame({"Instructor": graph_data['instructors'],
                           "Duration": graph_data['duration']},)
    table = df.pivot_table(index=["Instructor"], values="Duration", aggfunc=numpy.sum)
    sorted_table = table.sort_values("Duration", ascending=False)
    sender_email = peloton_param["sender_email"]
    receiver_email = peloton_param["receiver_email"]
    password = peloton_param["password"]

    # Create the HTML message
    subject = "Peloton Notifier"
    html_body = sorted_table.to_html()
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(html_body, "html"))

    # Establish a secure connection with the SMTP server
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        # Log in to the Gmail account
        server.login(sender_email, password)

        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())

    print("HTML Email sent successfully.")
    return


if __name__ == '__main__':
    lambda_handler(None, None)
