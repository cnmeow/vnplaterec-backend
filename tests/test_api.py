import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import io
import pytest

from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'tests/uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    yield app.test_client()
    
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
   
def test_predict_no_file(client):
    response = client.post('/predict', data={})
    assert response.status_code == 200
    assert b"No file" in response.data

def test_predict_no_user_id(client):
    data = {
        'image': (io.BytesIO(b"fake image data"), 'test.jpg')
    }
    response = client.post('/predict', data=data, content_type='multipart/form-data')
    assert b"Not found user id" in response.data

def test_predict_wrong_extension(client):
    data = {
        'image': (io.BytesIO(b"fake file"), 'test.txt'),
        'id_user': '123'
    }
    response = client.post('/predict', data=data, content_type='multipart/form-data')
    assert b"File type not supported" in response.data

def test_get_image_existing_file(client):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'dummy.jpg')
    with open(file_path, 'wb') as f:
        f.write(b'\xff\xd8\xff\xe0' + b'fake image content') 

    response = client.get('/images/dummy.jpg')
    
    assert response.status_code == 200
    assert response.content_type == 'image/jpeg'
    assert b'fake image content' in response.data
