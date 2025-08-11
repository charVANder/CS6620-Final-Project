# imports
import pytest
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mock_api.mock_drugbank import app, data

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_basic_mock_api():
    assert app is not None

def test_data_loads():
    assert len(data) > 0
    assert 'drug_name' in data[0]
    assert 'partner_drug_name' in data[0]
    assert 'severity' in data[0]
    assert 'description' in data[0]

def test_drug_search_found(client):
    response = client.get('/api/drugs/search?name=warfarin')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'drugs' in result
    assert len(result['drugs']) > 0

def test_drug_search_partial_match(client):
    response = client.get('/api/drugs/search?name=lor')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'drugs' in result # should find drugs with 'lor'

def test_empty_search(client):
    response = client.get('/api/drugs/search?name=')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'drugs' in result

def test_case_sensitivity(client):
    response1 = client.get('/api/drugs/search?name=lorazepam')
    response2 = client.get('/api/drugs/search?name=LORAZEPAM')
    assert response1.status_code == 200
    assert response2.status_code == 200

def test_interaction_check_found(client):
    response = client.get('/api/interactions/check?drug1=lorazepam&drug2=levetiracetam')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['interaction_found'] == True
    assert result['severity'] == 'moderate'

def test_interaction_check_not_found(client):
    response = client.get('/api/interactions/check?drug1=blah1&drug2=blah2')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['interaction_found'] == False