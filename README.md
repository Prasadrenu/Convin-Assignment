# Convin-Assignment

# Daily Expenses Project

## Overview

This Django-based project manages user information and tracks expenses. It includes functionalities for creating users, adding expenses, and generating balance sheets.

## Setup and Installation

### Prerequisites

- Python 3.x
- Django 4.x
- mysqlclient
- "openpyxl" library for handling Excel files

### Installation

1. **Clone the Repository**

   
   git clone https://github.com/Prasadrenu/Convin Assignment.git
   or  Download zip files from the repository

3.Create and Activate a Virtual Environment

  Command - python3 -m venv env
  source env/bin/activate  # For Unix-based systems
  env\Scripts\activate     # For Windows

4. Move to project directory

    cd daily_expenses

5.Generate requirements.txt

  pip install -r requirements.txt

6.Apply Migrations

  python manage.py makemigrations or python3 manage.py makemigrations 
  python manage.py migrate or python3 manage.py migrate

7.Run the Development Server

  python manage.py runserver or python3 manage.py runserver

8.To test the end points using postman

  First the end point should have "http://127.0.0.1:8000/" to direct  the port number where the server is running
  then add the below API endpoints according to the requirement

  POST /create_user:   # Create a new user.
  GET /user_details/<int:user_id>:     # Retrieve user details and <int:user_id> takes id of the user while creating user in User model
  
  POST /add/:     # Add expenses.
  GET /user/<int:user_id>/:   # Retrieve user expenses.
  GET /overall/:       # Retrieve all expenses.
  GET /download/<int:user_id>/:     #Download balance sheet

  Note: To download balance sheet run http://127.0.0.1:8000/download/<int:user_id>/ in the browser and you can open the .xlsx file and view the sheet in required fromat

9. To run Unit and Integration Tests

     python manage.py test



  




