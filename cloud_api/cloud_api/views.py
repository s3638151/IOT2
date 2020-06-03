"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import request, jsonify
from cloud_api import app
from cloud_api import db
from cloud_api.model import User, Rent_record, Car
import json
import uuid

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return "it is a restful api"


@app.route('/add_user', methods=['POST'])
def add_user(): 
    """add user into the system

    receive request in post, generate salted password hash
    then use ORM to add user in database

    Returns:
        return json status string, status is 0 means okay.
    """
    #app.logger.debug(request.get_json())
    params = json.loads(request.data)
    password = User.generate_salted_password_hash(params['password'])
    auser = User(params['username'],params['email'],params['firstname'],params['lastname'],password)
    db.session.add(auser)
    db.session.commit()
    return jsonify(status=0, message='ok')

@app.route('/login_user', methods=['POST'])
def login_user():    
    """check user login and password

    receive username and password from web layer post request. use validate_salted_password_hash 
    helper function to verify username and password


    Returns:
        return a json string to report result. status is 0 is okay, including username.
        otherwise, status is 1 including error message
    """

    params = json.loads(request.data)

    auser = User.query.filter_by(username=params['username']).first()
    if User.validate_salted_password_hash(params['password'],auser.password):
        return jsonify(status=0, username=auser.username)
    else:
        return jsonify(status=1, message='user name and password doesnot match')


@app.route('/list_rent_history/<username>', methods=['GET'])
def list_rent_history(username):    
    """list user's rent history

    Retrieve rent history for certain user. username as a parameter in part of URL
    response a json list of rent history including rent_id, username, pickup_ts, return_ts,
    unlock_ts, brand, body_type, year_manufactured fields.

    Returns:
        return a json string, status is 0 means okay. history is in data part
    """

    #app.logger.debug(request.get_json())
    query = db.session.query(Rent_record, Car).filter(Rent_record.car_id==Car.id).filter(Rent_record.username ==username)
    if query.count() == 0:
        return jsonify(status=0, data=None)

    data = []
    for r,c in query.all():
        data.append({"rent_id":r.id, "username":r.username, "pickup_ts":r.pickup_ts, "return_ts":r.return_ts, \
                     "unlock_ts":r.unlock_ts, "brand":c.brand, "body_type":c.body_type,"year_manufactured":c.year_manufactured})
    return jsonify(status=0, data=data)


@app.route('/list_available_cars', methods=['GET'])
def list_available_cars():  
    """list available cars in the system

    retrieve a list for all the available cars. 
    including id, brand, body_type, year_manufactured fields

    Returns:
        return value example {"status" = 0, data = {"id":"xxx", "brand":"BMW", "body_type":"small","year_manufactured":2000}}        
    """

    #app.logger.debug(request.get_json())
    query = db.session.query(Car).filter(Car.rent_id =="")
    if query.count() == 0:
        return jsonify(status=0, data=None)

    data = []
    for c in query.all():
        data.append({"id":c.id, "brand":c.brand, "body_type":c.body_type,"year_manufactured":c.year_manufactured})
    return jsonify(status=0, data=data)


@app.route('/book_a_car', methods=['POST'])
def book_a_car():   
    """book a car

    receive booking parameters from post including cardid, username, pickup_ts.  
    return status=0 and rent_id number if it is okay
    otherwise return status=1 and message for the error 

    Returns:
        return value example {"status" = 0, rent_id = "xxxyyyzzz"}
    """
    params = json.loads(request.data)
    query = db.session.query(Car).filter(Car.rent_id =="").filter(Car.id == params["carid"])
    if query.count() == 0:
        return jsonify(status=1, message='the car is not available for rent')

    id = uuid.uuid1()
    arecord = Rent_record(id, params["carid"], params['username'], "booked", params['pickup_ts'], None,None)
    db.session.add(arecord)
    db.session.commit()

    acar = db.session.query(Car).filter(Car.id==params["carid"]).first()
    acar.rent_id = id
    db.session.commit()

    return jsonify(status=0, rent_id=id)



@app.route('/return_a_car', methods=['POST'])
def return_a_car():
    """return a car

    receive booking parameters from post including username, password, rent_id, time(time to return)  
    return json string. status=0 if succeed. otherwise return status=1 or 2 with error message 

    Returns:
        return value example {"status" = 0}
        return value example {"status" = 1, "message"="user name and password doesnot match" }
        return value example {"status" = 2, "the rent record doesnot match" }
    """
    params = json.loads(request.data)

    auser = User.query.filter_by(username=params['username']).first()
    if not User.validate_salted_password_hash(params['password'],auser.password):
        return jsonify(status=1, message='user name and password doesnot match')

    query = db.session.query(Car,Rent_record).filter(Car.rent_id ==params["rent_id"]) \
            .filter(Car.id == Rent_record.car_id).filter(Rent_record.username == params['username'])
    if query.count() == 0:
        return jsonify(status=2, message='the rent record doesnot match')

    
    arecord =  db.session.query(Rent_record).filter(Rent_record.id==params["rent_id"]).first()
    arecord.status = "returned"
    arecord.return_ts = params['time']   
    db.session.commit()

    acar =  db.session.query(Car).filter(Car.id==arecord.card_id).first()
    acar.rent_id = ""
    db.session.commit()

    return jsonify(status=0)


@app.route('/unlock_a_car', methods=['POST'])
def unlock_a_car():    
    """return a car

    receive booking parameters from post including username, password, car_id, time(time to unlock)  
    return json string. status=0 if succeed. otherwise return status=1 or 2 with error message 

    Returns:
        return value example {"status" = 0}
        return value example {"status" = 1, "message"="user name and password doesnot match" }
        return value example {"status" = 2, "message"="the rent record doesnot match" }
    """

    params = json.loads(request.data)

    auser = User.query.filter_by(username=params['username']).first()
    if not User.validate_salted_password_hash(params['password'],auser.password):
        return jsonify(status=1, message='user name and password doesnot match')

    query = db.session.query(Car,Rent_record).filter(Car.id ==params["car_id"]) \
            .filter(Car.rent_id == Rent_record.id).filter(Rent_record.username == params['username'])\
            .filter(Rent_record.status=='booked')

    if query.count() == 0:
        return jsonify(status=2, message='the rent record doesnot match')

    
    acar =  db.session.query(Car).filter(Car.id==params["car_id"]).first()

    arecord =  db.session.query(Rent_record).filter(Rent_record.id==acard.rent_id).first()
    arecord.status = "in use"
    arecord.unlock_ts = params['time']   
    db.session.commit()       

    return jsonify(status=0)




@app.route('/cancel_a_book', methods=['POST'])
def cancel_a_book():
    """cancel a book

    receive booking parameters from post including car_id, rent_id  
    return json string. status=0 if succeed. otherwise return status=1  with error message 

    Returns:
        return value example {"status" = 0, message = "Sucessfully cancelled the booking"}
        return value example {"status" = 1, "message"="Cancellation cannot be done" }        
    """

    params = json.loads(request.data)
    query = db.session.query(Car, Rent_record).filter(Car.rent_id==params["carid"]).filter(Car.rent_id == Rent_record.id).filter(Rent_record.username==params["carid"])
        
    if query.count() == 0:
        return jsonify(status=1, message='Cancellation cannot be done')

    acar = db.session.query(Car).filter(Car.rent_id==params["rent_id"]).first()
    #in a car record, rent_id=="" means this car is avaiable for rent
    acar.rent_id = ""
    db.session.commit()

    arecord = db.session.query(Rent_record).filter(Rent_record.id==params["rent_id"]).first()
    arecord.status = "cancelled"
    db.session.commit()

    return jsonify(status=0, message = "Sucessfully cancelled the booking")


@app.route('/search_cars', methods=['POST'])
def search_cars():    
    """search_cars

    receive search parameters from post including brand, body_type, year_manufactured  
    return json string for a list of cars 

    Returns:
        return value example {"status" = 0, data = [{"id":"xxxyyyzzz", "brand":"BMW", "body_type":"small", "year_manufactured":2008}, {"id":"aaabbbccc", "brand":"GM", "body_type":"medium", "year_manufactured":2018}]}
        return value example {"status" = 0, data = null }        
    """

    params = json.loads(request.data)
    query = db.session.query(Car).filter(Car.rent_id =="").filter(Car.brand==params["brand"]).filter(Car.body_type==params["body_type"]).filter(Car.year_manufactured==params["year_manufactured"])
    if query.count() == 0:
        return jsonify(status=0, data=None)

    data = []
    for c in query.all():
        data.append({"id":c.id, "brand":c.brand, "body_type":c.body_type,"year_manufactured":c.year_manufactured})
    return jsonify(status=0, data=data)

    
@app.route('/test', methods=['GET'])
def test():
    return User.generate_salted_password_hash("abc")


