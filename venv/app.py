import json
from flask import Flask, render_template, request
import boto3

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def bugpage():
    if request.method == 'POST':
        #Get the details from the webform
        priority = request.form['priority']
        bug = request.form['name']
        description = request.form['description']

        #Store details in python dictionary
        data = {'name': bug, 'description': description}

        #Send the data dict and priority to choose the correct queue
        decideQueue(data, priority)

        message = 'Thank you for your submission'
        return render_template('webform.html', message=message)
    return render_template('webform.html')

#Decide on which queue the data needs to be sent to, based on priority
def decideQueue(data, priority):
    if priority == 'High':
        print("High if")
        sendToQueue(data, "HighPriority")
    elif priority == 'Medium' or priority == 'Low':
        print("Med/Low if")
        sendToQueue(data, 'MediumLowPriority')
    else:
        print("else")
        sendToQueue(data, 'DLQ')

    print(priority)

def sendToQueue(data, sqsQueue):
    # converts the python dict to a json
    jsonData = json.dumps(data)
    # creates the boto3 client
    sqs = boto3.client('sqs')
    # gets the queue url
    qURl = sqs.get_queue_url(QueueName=sqsQueue)['QueueUrl']
    # sends the message
    response = sqs.send_message(
        QueueUrl=qURl,
        DelaySeconds=10,
        MessageBody=(
            jsonData
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
