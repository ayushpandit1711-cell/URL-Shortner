# URL Shortener 🔗

A URL shortening service built with Python Flask and MySQL.
Just like bit.ly or tinyurl.com!

## Features
- ✂️ Shorten long URLs
- 🔍 Retrieve original URLs
- ✏️ Update existing short URLs
- 🗑️ Delete short URLs
- 📊 Track how many times a link was clicked

## Tech Stack
- Python + Flask
- MySQL Database
- HTML + CSS + JavaScript

## How to Run

### 1. Install packages
pip install -r requirements.txt

### 2. Setup MySQL database
mysql -u root -p < schema.sql

### 3. Update your MySQL password in app.py
app.config['MYSQL_PASSWORD'] = 'your_password'

### 4. Run the app
python app.py

### 5. Open in browser
http://localhost:5000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /shorten | Create short URL |
| GET | /shorten/<code> | Get URL info |
| PUT | /shorten/<code> | Update URL |
| DELETE | /shorten/<code> | Delete URL |
| GET | /shorten/<code>/stats | Get click stats |

https://roadmap.sh/projects/url-shortening-service
 
## Made by
Ayush — Built from scratch as a beginner Python project! 🚀
