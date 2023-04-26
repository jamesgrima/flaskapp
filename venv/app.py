import json
from flask import Flask, render_template, request
import boto3

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def bugpage():
    if request.method == 'POST':
        priority = request.form['priority']
        bug = request.form['name']
        description = request.form['description']

        data = {'name': bug, 'description': description}

        if priority == 'High':
            sendToQueue(data, "HighPriority")
        elif priority == 'Medium' or 'Low':
            sendToQueue(data, 'MediumLowPriority')
        else:
            sendToQueue(data, 'DLQ')

    return render_template('webform.html')

def sendToQueue(payload, sqsQueue):
    # converts the python dict to a json
    jsonPayload = json.dumps(payload)
    # creates the boto3 client
    sqs = boto3.client('sqs')
    # gets the queue url
    qURl = sqs.get_queue_url(QueueName=sqsQueue)['QueueUrl']
    # sends the message
    response = sqs.send_message(
        QueueUrl=qURl,
        DelaySeconds=10,
        MessageBody=(
            jsonPayload
        )
    )

@app.route('/createQueues')
def setUpSQSQueues():
    sqs = boto3.client('sqs')
    queNames = ['HighPriority', 'MediumLowPriority', 'DLQ']
    for queName in queNames:
        sqs.create_queue(QueueName=queName, Attributes={'DelaySeconds': '60'})
    return render_template("webform.html")

@app.route('/destroyQueues')
def destroyQueues():
    # creates the boto3 client
    sqs = boto3.client('sqs')
    queueNames = ['HighPriority', 'MediumLowPriority', 'DLQ']
    for queueName in queueNames:
        qURl = sqs.get_queue_url(QueueName=queueName)['QueueUrl']
        sqs.delete_queue(QueueUrl=qURl)
    return render_template("webform.html")

if __name__ == '__main__':
    app.run()
