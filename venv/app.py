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
        filename = priority.lower() + '.json'
        if priority == 'Select Priority':
            filename = 'dlq.json'
        data = {'name': bug, 'description': description}
        with open(filename, 'a') as f:
            json.dump(data, f)
            f.write('\n')
    return render_template('webform.html')

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

if __name__ == '__main__':
    app.run()
