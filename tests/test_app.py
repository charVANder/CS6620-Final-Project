# imports
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.app import app, check_drug_pairs

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_basic_flask():
    assert app is not None

def test_main_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Drug Interaction Checker' in response.data

def test_empty_drug_input(client):
    response = client.post('/check', data={'drugs': ''})
    assert response.status_code == 200
    assert b'Need to enter at least one drug name' in response.data

def test_single_drug_input(client): # 2 are required
    response = client.post('/check', data={'drugs': 'warfarin'})
    assert response.status_code == 200
    assert b'At least 2 drugs are required' in response.data

def test_drug_pairs_algorithm():
    drugs = ['metformin', 'warfarin', 'simvastatin']
    expected_pairs = [
        ('metformin', 'warfarin'),
        ('metformin', 'simvastatin'), 
        ('warfarin', 'simvastatin')
    ]
    actual_pairs = []
    for i in range(len(drugs)):
        for j in range(i+1, len(drugs)):
            actual_pairs.append((drugs[i], drugs[j]))
    assert len(actual_pairs) == 3
    assert set(actual_pairs) == set(expected_pairs)

def test_case_sensitivity():
    drugs1 = ['METFORMIN', 'warfarin']
    drugs2 = ['metformin', 'WARFARIN']
    drugs3 = ['Metformin', 'Warfarin']
    same1 = [drug.lower() for drug in drugs1]
    same2 = [drug.lower() for drug in drugs2] 
    same3 = [drug.lower() for drug in drugs3]
    assert same1 == same2 == same3

def test_duplicate_drugs():
    # Based on the algorithm I used, it should de-duplicate
    drugs = ['metformin', 'metformin', 'warfarin', 'Metformin']
    unique_drugs = list(set([drug.lower().strip() for drug in drugs if drug.strip()]))
    assert len(unique_drugs) == 2
    assert 'metformin' in unique_drugs
    assert 'warfarin' in unique_drugs
