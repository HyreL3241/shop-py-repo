# Shoplift Project

## Overview
Shoplift is a Django-based web application that utilizes SQLite as its database and Bootstrap for the frontend. This project aims to provide a simple and responsive e-commerce platform.

## Project Structure
```
shoplift/
├── shoplift/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── manage.py
├── db.sqlite3
├── static/
│   ├── css/
│   │   └── bootstrap.min.css
│   ├── js/
│       └── bootstrap.bundle.min.js
├── templates/
│   └── base.html
└── README.md
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd shoplift
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install django
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**
   Open your web browser and go to `http://127.0.0.1:8000/`.

## Usage
You can start building your e-commerce features by modifying the views and templates. The project is set up to use Bootstrap for styling, making it easy to create a responsive design.

## License
This project is licensed under the MIT License.