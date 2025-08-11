# imports
from flask import Flask, render_template, request
import serverless_wsgi
import boto3
import requests
# import json
import os
# from datetime import datetime, timedelta

app = Flask(__name__)

#MOCK_API_URL = "http://mock-api:5001"
MOCK_API_URL = os.environ.get('MOCK_API_URL', 'http://mock-api:5001')
CACHE_TABLE = "drug-interactions-cache"


dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566', aws_access_key_id='test', aws_secret_access_key='test', region_name='us-east-1')

@app.route('/')
def index():
    return render_template('index.html')

# maybe adding CORS stuff might help???? TT_TT
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route('/check', methods=['POST'])
def check_interactions():
    drug_names = request.form.get("drugs", "").strip()
    if not drug_names:
        return render_template('index.html', error="Need to enter at least one drug name")
    drugs = [drug.strip() for drug in drug_names.replace(',', '\n').split('\n') if drug.strip()]
    if len(drugs) < 2:
        return render_template('index.html', error="At least 2 drugs are required to check interactions")
    interactions = check_drug_pairs(drugs) # make this a separate function
    return render_template('results.html', drugs=drugs, interactions=interactions)

def check_drug_pairs(drugs):
    interactions = []

    # n choose 2/triange method for getting pairs
    for i in range(len(drugs)):
        for j in range(i+1, len(drugs)):
            drug1, drug2 = drugs[i], drugs[j]

            # call mock API (NOTE TO SELF: add cacheing later)
            try:
                response = requests.get(f"{MOCK_API_URL}/api/interactions/check", params={'drug1': drug1, 'drug2': drug2}, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    interaction_data = { # will use the drug_data.json format
                        'drug1': drug1,
                        'drug2': drug2,
                        'interaction_found': result.get('interaction_found', False),
                        'severity': result.get('severity', 'unknown'),
                        'description': result.get('description', 'No description available')
                    }
                    interactions.append(interaction_data)      
            except Exception as e:
                interactions.append({
                    'drug1': drug1,
                    'drug2': drug2,
                    'interaction_found': False,
                    'error': f"Error: {str(e)}"
                })
    return interactions

def lambda_handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

if __name__ == '__main__':
    app.run(debug=True, port=5000)