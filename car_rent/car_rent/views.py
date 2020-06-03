"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template,request, session
from car_rent import app

import requests
import json

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return "Home"


@app.route('/register', methods=['POST'])
def register():
    """register user in the system

    receive user input in post request, transfer request in json format to API cloud restful interface
    then get response from API cloud and render template page register.html

    Returns:
        rendered template register.html
    """
    headers = {'Content-Type': 'application/json'}   
    r = requests.post(url=app.config['CLOUD_API_URL']+"add_user", headers=headers, json=request.form)
    
    result  = json.loads(r.content)
    return render_template('register.html',result = result)


@app.route('/login', methods=['POST'])
def login():
    """login user into the system

    receive username and password from post parameters. send back to API cloud to validate.
    fail to verify, response front end with result message.
    succeed to verify, save username in session object for future usage and response with
    rendered index.html

    Returns:
        rendered template index.html
    """
    headers = {'Content-Type': 'application/json'}   
    r = requests.post(url=app.config['CLOUD_API_URL']+"login_user", headers=headers, json=request.form)
    result  = json.loads(r.content)
    
    if (result["status"]!=0):
        return result['message']
    
    session['username'] = result['username']
    return render_template('index.html')


@app.route('/list_available_cars', methods=['GET'])
def list_available_cars():    
    """list available cars in the system

    request api back end for all the available cars. API service response with information
    in json format
    render template list_available_cars.html with data

    Returns:
        rendered template list_available_cars.html
    """

    #headers = {'Content-Type': 'application/json'}   
    r = requests.get(url=app.config['CLOUD_API_URL']+"list_available_cars")
    result  = json.loads(r.content)
    return render_template('list_available_cars.html',data_list=result['data'])


@app.route('/search_cars', methods=['POST'])
def search_cars():    
    """search cars

    receive search parameters from post. send back to API cloud to search
    fail to verify, response front end with result message.
    succeed to verify, save username in session object for future usage and response with
    rendered index.html

    Returns:
        rendered template search_cars.html
    """
    headers = {'Content-Type': 'application/json'}   
    r = requests.get(url=app.config['CLOUD_API_URL']+"search_cars",headers=headers, json=request.form )
    result  = json.loads(r.content)
    return render_template('search_cars.html',data_list=result['data'])


@app.route('/book_a_car', methods=['POST'])
def book_a_car():
    """book a car

    receive booking parameters from post. send back to API cloud to book, 
    response front end with result message.
    rendered book_a_car.html

    Returns:
        rendered template book_a_car.html
    """
    headers = {'Content-Type': 'application/json'}   
    params ={"username":session['username'], "carid":request.form['carid'],"pickup_ts":request.form['pickup_ts']}
    r = requests.get(url=app.config['CLOUD_API_URL']+"book_a_car", headers=headers, json = json.dumps(params))
    result  = json.loads(r.content)
    return render_template('book_a_car.html',result=result)


@app.route('/cancel_a_book', methods=['POST'])
def cancel_a_book():    
    """cancel a car booking

    Cancel a booking. send back post parameters to API cloud.
    response front end with result message.
    rendered book_a_car.html

    Returns:
        rendered template book_a_car.html
    """
    headers = {'Content-Type': 'application/json'}   
    params ={"username":session['username'], "rent_id":request.form['rent_id']}
    r = requests.get(url=app.config['CLOUD_API_URL']+"cancel_a_book", headers=headers, json = json.dumps(params))
    result  = json.loads(r.content)
    return render_template('cancel_a_book.html',message=result['message'])


@app.route('/list_rent_history', methods=['GET'])
def list_rent_history():
    """list user's rent history

    Call API cloud service to retrieve use rent history.
    response front end with result message in  list_rent_history.html

    Returns:
        rendered template list_rent_history.html
    """
    #headers = {'Content-Type': 'application/json'}   
    r = requests.get(url=app.config['CLOUD_API_URL']+"list_rent_history/"+session['username'])
    result  = json.loads(r.content)
    return render_template('list_rent_history.html',data_list=result['data'])


@app.route('/logout', methods=['GET'])
def logout():
    """logout user 

    clear up use session information

    Returns:
        rendered template logout.html
    """

    # remove the username from the session if it's there
    session.pop('username', None)
    return render_template('logout.html')


@app.route('/test', methods=['GET'])
def test():
    return app.config['CLOUD_API_URL']
