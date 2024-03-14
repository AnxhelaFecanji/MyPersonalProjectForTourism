from flask_app import app
from flask import render_template, request, session, redirect, flash,jsonify
from flask_bcrypt import Bcrypt 
from flask_app.models.business import Business
from flask_app.models.visitor import Visitor
from flask_app.models.attraction import Attraction
from flask_app.models.activity import Activity


bcrypt = Bcrypt(app)
from datetime import datetime
from urllib.parse import unquote
UPLOAD_FOLDER = 'flask_app/static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import os
from werkzeug.exceptions import RequestEntityTooLarge

from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from werkzeug.exceptions import HTTPException, NotFound
import urllib.parse

import smtplib


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
@app.route('/visitor')
def indexVisitor():
    if 'visitor_id' in session:
        return redirect('/visitor/dashboard')
    return redirect('/logout')

@app.route('/register/visitor', methods = ['POST'])
def register():
    if 'visitor_id' in session:
        return redirect('/visitor')
    if not Visitor.validate_visitorRegister(request.form):
        return redirect(request.referrer)
    visitor = Visitor.get_visitor_by_email(request.form)
    if visitor:
        flash('This account already exists', 'visitorEmailRegister')
        return redirect(request.referrer)
    
    data = {
        'firstName': request.form['firstName'],
        'lastName': request.form['lastName'],
        'email': request.form['email'],
        'password': bcrypt.generate_password_hash(request.form['password'])
    }
    session['visitor_id'] = Visitor.create_visitor(data)
    return redirect('/visitor')

@app.route('/loginPageRegister/visitor')
def loginPageVisitor():
    if 'visitor_id' in session:
        return redirect('/visitor/dashboard')
    return render_template('visitorLoginRegister.html')

@app.route('/login/visitor', methods = ['POST'])
def loginVisitor():
    if 'visitor_id' in session:
        return redirect('/visitor')
    if not Visitor.validate_visitor(request.form):
        return redirect(request.referrer)
    visitor = Visitor.get_visitor_by_email(request.form)
    if not visitor:
        flash('This email doesnt exist', 'visitorEmailLogin')
        return redirect(request.referrer)
    
    if not bcrypt.check_password_hash(visitor['password'], request.form['password']):
        flash('Incorrect password', 'visitorPasswordLogin')
        return redirect(request.referrer)
    
    session['visitor_id']= visitor['id']
    return redirect('/visitor')

@app.route('/visitor/dashboard')
def dashboardVisitor():
    if 'visitor_id' not in session:
        return redirect('/visitor')
    data = {
        'id': session['visitor_id']
    }
    visitor=Visitor.get_visitor_by_id(data)
    businesses = Business.get_all_businesses()
    attractions = Attraction.get_all_attractions()
    activities = Activity.get_all_activities()
    return render_template('visitordashboard.html', visitor = visitor, businesses=businesses, attractions=attractions, activities=activities)

@app.route('/visitor/business/<int:id>')
def showOneBusiness(id):
    if 'visitor_id' not in session:
        return redirect('/visitor')
    data = {
        'id': id
    }
    
    business = Business.get_business_by_id(data)
    
    return render_template('visitorViewBusiness.html', business=business)

@app.route('/visitor/attraction/<int:id>')
def showOneAttraction(id):
    if 'visitor_id' not in session:
        return redirect('/visitor')
    data = {
        'id': id
    }
    
    attraction = Attraction.get_attraction_by_id(data)
    
    return render_template('visitorViewOneAttraction.html', attraction=attraction)

@app.route('/visitor/activity/<int:id>')
def showOneActivity(id):
    if 'visitor_id' not in session:
        return redirect('/visitor')
    data = {
        'id': id
    }
    
    activity = Activity.get_activity_by_id(data)
    
    return render_template('visitorViewOneActivity.html', activity=activity)

@app.route('/visitor/myposts')
def showAllPosts():
    if 'visitor_id' not in session:
        return redirect('/visitor')
    
    data = {
        'id': session['visitor_id']
    }
    visitor = Visitor.get_visitor_by_id(data)
    posts = Attraction.get_all_postsAttractions()
    postsActivities = Activity.get_all_postsActivities()
    businesses = Business.get_all_postsBusinesses()
    return render_template('visitorAllPosts.html', posts=posts, postsActivities=postsActivities, businesses=businesses, visitor=visitor)