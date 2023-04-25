import json
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def bugpage():
    if request.method == 'POST':
        priority = request.form['priority']
        bug = request.form['name']
        description = request.form['description']
        filename = priority.lower() + '.json'
        data = {'name': bug, 'description': description}
        with open(filename, 'a') as f:
            json.dump(data, f)
            f.write('\n')
    return render_template('webform.html')

if __name__ == '__main__':
    app.run()
