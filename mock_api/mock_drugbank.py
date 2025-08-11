# imports
from flask import Flask, jsonify, request
import json
import time
import random
import os
script_dir = os.path.dirname(os.path.abspath(__file__)) # adding this for testing to work
data_path = os.path.join(script_dir, 'drug_data.json')

app = Flask(__name__)

with open(data_path, 'r') as file:
    data = json.load(file)

@app.route('/api/drugs/search')
def search_drugs():
    req = request.args.get('name', '').lower()

    # adding something to simulate api delay
    time.sleep(random.uniform(0.1, 0.5))

    matches = []
    seen = set()
    for interaction in data:
        if req in interaction['drug_name'].lower() and interaction['drug_name'] not in seen:
            matches.append({"name": interaction['drug_name'], "id": interaction['drug_id']})
            seen.add(interaction['drug_name'])
        if req in interaction['partner_drug_name'].lower() and interaction['partner_drug_name'] not in seen:
            matches.append({"name": interaction['partner_drug_name'], "id": interaction['partner_drug_id']})
            seen.add(interaction['partner_drug_name'])
    return jsonify({"drugs": matches})


@app.route('/api/interactions/check')
def check_interactions():
    drug1 = request.args.get("drug1", "").lower()
    drug2 = request.args.get("drug2", "").lower()

    # adding something to simulate api delay
    time.sleep(random.uniform(0.1, 0.5))

    for interaction in data:
        name1 = interaction["drug_name"].lower()
        name2 = interaction["partner_drug_name"].lower()
        if (name1 == drug1 and name2 == drug2) or (name1 == drug2 and name2 == drug1):
            return jsonify({
                "interaction_found": True,
                "severity": interaction["severity"],
                "description": interaction["description"]
            })
    return jsonify({"interaction_found": False})
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)