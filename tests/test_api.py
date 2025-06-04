import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import io
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app
import shutil

UPLOAD_FOLDER = 'images'
@pytest.fixture(scope="module")
def client():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    with TestClient(app) as test_client:
        yield test_client
    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)

def test_predict_no_file(client):
    response = client.post("/predict", files={}, data={})
    assert response.status_code == 400 or response.status_code == 422

def test_predict_no_user_id(client):
    files = {
        'image': ('test.jpg', io.BytesIO(b"fake image data"), 'image/jpeg')
    }
    response = client.post("/predict", files=files)
    assert response.status_code == 400 or response.status_code == 422

def test_predict_wrong_extension(client):
    files = {
        'image': ('test.txt', io.BytesIO(b"fake file data"), 'text/plain')
    }
    data = {'id_user': '123'}
    response = client.post("/predict", files=files, data=data)
    assert response.status_code == 400 or response.status_code == 422
    assert "File type not supported" in response.json()["error"]

def test_get_image_existing_file(client):
    file_path = os.path.join(UPLOAD_FOLDER, 'dummy.jpg')
    content = b'\xff\xd8\xff\xe0' + b'fake image content'
    with open(file_path, 'wb') as f:
        f.write(content)

    response = client.get("/images/dummy.jpg")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert content in response.content