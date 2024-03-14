from flask_app import app
from flask import render_template, redirect, flash, session, request, url_for
from flask_bcrypt import Bcrypt

from flask_app.models.admin import Admin
from flask_app.models.owner import Owner
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

@app.route('/')
def indexmain():
    if 'user_id' in session:
        return redirect('/admin')
    return render_template('mainPage.html')
    
@app.route('/admin')
def indexadmin():
    if 'user_id' in session:
        return redirect('/admin/dashboard')
    return redirect('/logout')

@app.route('/loginPage/admin')
def loginPageAdmin():
    if 'user_id' in session:
        return redirect('/admin')
    return render_template('adminLogin.html')

@app.route('/login/admin', methods = ['POST'])
def loginAdmin():
    if 'user_id' in session:
        return redirect('/admin')
    if not Admin.validate_admin(request.form):
        return redirect(request.referrer)
    user = Admin.get_admin_by_email(request.form)
    if not user:
        flash('This email doesnt exist', 'emailLoginAdmin')
        return redirect(request.referrer)
    if not bcrypt.check_password_hash(user['password'], request.form['password']):
        flash('Incorrect password', 'passwordLoginAdmin')
        return redirect(request.referrer)
    
    session['user_id']= user['id']
    return redirect('/admin/dashboard')

@app.route('/admin/dashboard')
def adminPage():
    if 'user_id' not in session:
        return redirect('/admin')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    businessOwners = Owner.get_all_owners()
    attractions = Attraction.get_all_attractions()
    activities = Activity.get_all_activities()
    payments = Owner.get_allPayments()
    if admin and admin['role'] == 'admin':
        return render_template('adminDashboard.html', loggedUser = admin, businessOwners= businessOwners, attractions=attractions, activities=activities, payments=payments)
    return redirect('/logout')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/admin/businessOwner/new')
def newBusinessOwner():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        return render_template('registerBusinessOwner.html')
    return redirect('/logout')

@app.route('/admin/register/businessOwner', methods = ['POST'])
def registerBusinessOwner():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        if not Owner.validate_ownerRegister(request.form):
            return redirect(request.referrer)
        owner = Owner.get_owner_by_email(request.form)
        if owner:
            flash('This account already exists', 'ownerEmailRegister')
            return redirect(request.referrer)
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': bcrypt.generate_password_hash(request.form['password']),
            'phone': request.form['phone']
        }
        Owner.create_owner(data)
        flash('Buisness Owner created successfully', 'ownerSuccessRegister')
        return redirect(request.referrer)
    return redirect('/')

@app.route('/admin/attraction/new')
def newAttraction():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        return render_template('newAttraction.html')
    return redirect('/logout')

@app.route('/admin/add/attraction', methods = ['POST'])
def addAttraction():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        if not Attraction.validate_attraction(request.form):
            return redirect(request.referrer)
    if 'images' not in request.files:
        flash('Please upload an image', 'imagesAttraction')
        return redirect(request.referrer)
    attractionImages = request.files.getlist('images')
    image_filenames = []
    for attractionImage in attractionImages:
        if not allowed_file(attractionImage.filename):
            flash('The file should be in png, jpg or jpeg format!', 'imagesAttraction')
            return redirect(request.referrer)
    
        if attractionImage:
            filename1 = secure_filename(attractionImage.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename1
            filename1 = time
            attractionImage.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            image_filenames.append(filename1)
            
    images_string = ','.join(image_filenames)
    data = {
        'name': request.form['name'],
        'type': request.form['type'],
        'address': request.form['address'],
        'description': request.form['description'],
        'images': images_string
    }
    Attraction.create_attraction(data)
    flash('Attraction created successfully', 'attractionSuccessRegister')
    return redirect(request.referrer)

@app.route('/admin/attraction/<int:id>')
def oneAttraction(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        
        'id': id
    }
 
        
    attraction = Attraction.get_attraction_by_id(data)
    return render_template('adminViewAttraction.html', attraction=attraction)
    

@app.route('/admin/attraction/edit/<int:id>')
def attractionEdit(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        
        'id': id
    }
   
    attraction = Attraction.get_attraction_by_id(data)
    return render_template('editAttraction.html', attraction=attraction)

@app.route('/admin/attraction/update/<int:id>', methods = ['POST'])
def updateAttraction(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'user_id': session['user_id'],
        'id': id
        
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        if not Attraction.validate_updateAttraction(request.form):
            return redirect(request.referrer)
    if 'images' not in request.files:
        flash('Please upload an image', 'imagesAttraction')
        return redirect(request.referrer)
    attractionImages = request.files.getlist('images')
    image_filenames = []
    for attractionImage in attractionImages:
        if not allowed_file(attractionImage.filename):
            flash('The file should be in png, jpg or jpeg format!', 'imagesAttractionupdated')
            return redirect(request.referrer)
    
        if attractionImage:
            filename1 = secure_filename(attractionImage.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename1
            filename1 = time
            attractionImage.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            image_filenames.append(filename1)
            
    images_string = ','.join(image_filenames)
    data = {
        'name': request.form['name'],
        'type': request.form['type'],
        'description': request.form['description'],
        'images': images_string,
        'id': id
    }
    Attraction.update_attraction(data)
    flash('Attraction updated successfully', 'attractionSuccessUpdated')
    return redirect(request.referrer)

@app.route('/admin/activity/new')
def newActivity():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        return render_template('newActivity.html')
    return redirect('/logout')

@app.route('/admin/add/activity', methods = ['POST'])
def addActivity():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        if not Activity.validate_activity(request.form):
            return redirect(request.referrer)
    if 'images' not in request.files:
        flash('Please upload an image', 'imagesActivity')
        return redirect(request.referrer)
    activityImages = request.files.getlist('images')
    activity_filenames = []
    for activityImage in activityImages:
        if not allowed_file(activityImage.filename):
            flash('The file should be in png, jpg or jpeg format!', 'imagesActivity')
            return redirect(request.referrer)
    
        if activityImage:
            filename1 = secure_filename(activityImage.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename1
            filename1 = time
            activityImage.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            activity_filenames.append(filename1)
            
    image_string = ','.join(activity_filenames)
    data = {
        'activity': request.form['activity'],
        'activityDate': request.form['activityDate'],
        'duration': request.form['duration'],
        'location': request.form['location'],
        'description': request.form['description'],
        'images': image_string
    }
    Activity.create_activity(data)
    flash('Activity created successfully', 'activitySuccessRegister')
    return redirect(request.referrer)

@app.route('/admin/activity/<int:id>')
def oneActivity(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        
        'id': id
    }

    activity = Activity.get_activity_by_id(data)
    return render_template('adminViewActivity.html', activity=activity)


@app.route('/admin/activity/edit/<int:id>')
def activityEdit(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        
        'id': id
    }

    activity = Activity.get_activity_by_id(data)
    return render_template('editActivity.html', activity=activity)

@app.route('/admin/activity/update/<int:id>', methods = ['POST'])
def updateActivity(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'user_id': session['user_id'],
        'id': id
        
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        if not Activity.validate_updateActivity(request.form):
            return redirect(request.referrer)
    if 'images' not in request.files:
        flash('Please upload an image', 'imagesActivityupdated')
        return redirect(request.referrer)
    activityImages = request.files.getlist('images')
    activity_filenames = []
    for activityImage in activityImages:
        if not allowed_file(activityImage.filename):
            flash('The file should be in png, jpg or jpeg format!', 'imagesActivityupdated')
            return redirect(request.referrer)
    
        if activityImage:
            filename1 = secure_filename(activityImage.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename1
            filename1 = time
            activityImage.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            activity_filenames.append(filename1)
            
    image_string = ','.join(activity_filenames)
    data = {
        'activity': request.form['activity'],
        'activityDate': request.form['activityDate'],
        'duration': request.form['duration'],
        'location': request.form['location'],
        'description': request.form['description'],
        'images': image_string,
        'id': id
    }
    Activity.update_activity(data)
    flash('Activity updated successfully', 'activitySuccessUpdated')
    return redirect(request.referrer)