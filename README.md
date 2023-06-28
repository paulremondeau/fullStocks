# A web application for stocks information
This repo contains a full-stack web-application for visualize various stock information.

The backend is made in Python using Flask.

The frontend is made in Vue 3.

The free stock prices API is the free tier Twelve Data (max 8 requests per minute)
Data update frequency is set to 8h

App link : https://fullstocks.onrender.com/ (reload maybe first time if back end went in sleep mode)

# How to run locally

## 1. Backend

Tested for Python 3.11.3

Create backend/config.py with the following :

```python

API_KEY = "your_twelve_data_api_key"
API_PLAN = "Basic"
FRONTEND_URL = "http://192.168.1.15:8080" # Change for your frontend URL
```

In the backend folder, run
```bash
$ pip install -r requirements.txt
```
```bash
$ python app.py
```

## 2. Frontend

Test for Node.js v18.16.0

Create frontend/config.js with the following :


```javascript
const apiUrl = "http://localhost:5000/" // Change for your backend URL

export default apiUrl
```

In the frontend folder, run

```bash
npm install
```

```bash
npm run dev
```