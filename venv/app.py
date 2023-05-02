import json
from flask import Flask, render_template, request
import boto3

#Creates the Flask app
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def bug_page():
    if request.method == 'POST':
        #Get the details from the webform
        priority = request.form['priority']
        bug = request.form['name']
        description = request.form['description']

        #Store details in a dictionary
        data = {'name': bug, 'description': description}

        #Send the data dict and priority to choose the correct queue
        decide_queue(data, priority)

        #Set the user feedback message
        message = 'Thank you for your submission'

        return render_template('webform.html', message=message)
    return render_template('webform.html')

#Decide on which queue the data needs to be sent to, based on priority
def decide_queue(data, priority):
    if priority == 'High':
        send_to_queue(data, "HighPriority")
    elif priority == 'Medium' or priority == 'Low':
        send_to_queue(data, 'MediumLowPriority')
    else:
        send_to_queue(data, 'DLQ')

#Send the data to given AWS SQS queue
def send_to_queue(data, sqsQueue):
    #Converts the python dictionary to a json
    json_data = json.dumps(data)

    #Creates the boto3 client
    sqs = boto3.client('sqs')

    #Gets the queue url
    queue_url = sqs.get_queue_url(QueueName=sqsQueue)['QueueUrl']

    #Sends the message to the queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageBody=(
            json_data
        )
    )

@app.route('/createQueues')
def setup_sqs_queues():
    sqs = boto3.client('sqs')
    queue_names = ['HighPriority', 'MediumLowPriority', 'DLQ']
    for queue in queue_names:
        sqs.create_queue(QueueName=queue, Attributes={'DelaySeconds': '60'})
    return render_template("webform.html")

@app.route('/destroyQueues')
def destroy_queues():
    # creates the boto3 client
    sqs = boto3.client('sqs')
    queue_names = ['HighPriority', 'MediumLowPriority', 'DLQ']
    for queue in queue_names:
        q_url = sqs.get_queue_url(QueueName=queue)['QueueUrl']
        sqs.delete_queue(QueueUrl=q_url)
    return render_template("webform.html")

if __name__ == '__main__':
    app.run()
