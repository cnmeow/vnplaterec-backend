# 🚗 Vietnam License Plate Recognition - Backend 

This backend service provides an API for detecting license plates from uploaded images or live camera feed. Built with Flask and powered by AI models like YOLO and Faster R-CNN.
 
👉 **Frontend repository:** [github.com/cnmeow/vnplaterec-frontend](https://github.com/cnmeow/vnplaterec-frontend)

## ✨ Features

- Upload images to recognize license plates 

  <img width="600" alt="image" src="https://github.com/user-attachments/assets/2c7e742f-776d-4e83-ae53-7cb76fc37834" />
- Real-time recognition from live camera feed

  <img width="600" alt="image" src="https://github.com/user-attachments/assets/3a3ab07e-7c94-4c5b-8842-10feafd537b4" />

## 🚀 Getting Started

### Run Backend
1. Clone the Backend Repository
```bash
git clone https://github.com/cnmeow/vnplaterec-backend.git
cd vnplaterec-backend
```

2. Run
- Option A: Run with Python (Flask)
  ```bash
  # Create virtual environment (optional)
  python -m venv venv
  source venv/bin/activate # (macOS)
  venv\Scripts\activate.bat # (Windows)

  
  # Install dependencies
  pip install -r requirements.txt
  
  # Run the Flask server
  gunicorn main:app --bind 0.0.0.0:8080
  ```

- Option B: Run with Docker
  ```bash
  # Build Docker image
  docker build -t vnplaterec-backend .

  # Run Docker container
  docker run -d -p 8080:8080 --name vnplaterec-backend vnplaterec-backend
  ```

🟢 Backend running at: `http://localhost:8080`

### Run Frontend
1. Clone the Frontend Repository
```bash
git clone https://github.com/cnmeow/vnplaterec-frontend.git
cd vnplaterec-frontend
```

2. Run
- Option A: Run with npm
  - Install Dependencies
    ```bash
    npm install
    ```
  - Create `.env`
    ```bash
    NEXT_PUBLIC_API_URL=http://localhost:8080 # Backend
    ```
  - Start Development Server
    ```bash
    npm run dev
    ```

- Option B: Run with Docker
  ```bash
  # Build Docker image
  docker build -t vnplaterec-frontend .

  # Run Docker container
  docker run -d -p 3000:3000 --name vnplaterec-frontend vnplaterec-frontend
  ```

🟢 Frontend running at: `http://localhost:3000`
