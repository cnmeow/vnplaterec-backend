import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import io
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app
import shutil
from PIL import Image
import numpy as np
import cv2

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'images'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with TestClient(app) as c:
        yield c
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
   
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert "ok" in response.json()["status"]

def test_predict_without_file(client):
    response = client.post("/predict", data={'id_user': '123'})
    assert response.status_code == 400 or response.status_code == 422
    if response.status_code == 400:
        assert "No file part" in response.json()["error"]
    else:
        assert "detail" in response.json()

def test_predict_with_file_noname(client):
    files = {
        'image': ('', io.BytesIO(b"fake image data"), 'image/jpeg')
    }
    response = client.post("/predict", files=files, data={'id_user': '123'})
    assert response.status_code == 400 or response.status_code == 422
    if response.status_code == 400:
        assert "No file" in response.json()["error"]
    else:
        assert "detail" in response.json()

def test_predict_wrong_extension(client):
    files = {
        'image': ('test.txt', io.BytesIO(b"fake file data"), 'text/plain')
    }
    data = {'id_user': '123'}
    response = client.post("/predict", files=files, data=data)
    assert response.status_code == 400 or response.status_code == 422
    assert "File type not supported" in response.json()["error"]

def test_predict_no_user_id(client):
    files = {
        'image': ('test.jpg', io.BytesIO(b"fake image data"), 'image/jpeg')
    }
    response = client.post("/predict", files=files)
    assert response.status_code == 400 or response.status_code == 422
    if response.status_code == 400:
        assert "User ID is required" in response.json()["error"]
    else:
        assert "detail" in response.json()

def test_predict_user_id_spaces(client):
    files = {
        'image': ('test.jpg', io.BytesIO(b"fake image data"), 'image/jpeg')
    }
    response = client.post("/predict", files=files, data={'id_user': '   '})
    assert response.status_code == 400 or response.status_code == 422
    assert "User ID is required" in response.json()["error"]

def test_predict_empty_file(client):
    files = {
        'image': ('empty.jpg', io.BytesIO(b""), 'image/jpeg')
    }
    response = client.post("/predict", files=files, data={'id_user': '123'})
    assert response.status_code == 400 or response.status_code == 422
    assert "Empty file" in response.json()["error"]

def test_predict_valid_file(client):
    sample_image_path = os.path.join(os.path.dirname(__file__), 'test.jpg')
    with open(sample_image_path, "rb") as f:
        img_bytes = f.read()
    files = {
        'image': ('test.jpg', io.BytesIO(img_bytes), 'image/jpeg')
    }
    response = client.post("/predict", files=files, data={'id_user': 'test'})
    assert response.status_code == 200
    assert 'result_path' in response.json() 
    assert 'plate_text' in response.json()
    assert 'run_time' in response.json()
