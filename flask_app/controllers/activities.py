from flask_app import app
from flask import render_template, redirect, flash, session, request, url_for
from flask_bcrypt import Bcrypt
from flask_app.models.activity import Activity
from flask_app.models.visitor import Visitor

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
           
@app.route('/visitor/activity/post/new/<int:id>')
def newpostActivity(id):
    if 'visitor_id' not in session:
        return redirect('/visitor')
    data = {
        
        'id': id
        
    }
    activity = Activity.get_activity_by_id(data)
    return render_template('visitorAddActivityPost.html', activity=activity)
           


@app.route('/visitor/activity/post/new/<int:id>', methods = ['POST'])
def createActivityPost(id):
    if 'visitor_id' not in session:
        return redirect('/visitor')
    data = {
        'id': session['visitor_id']
    }
    visitor = Visitor.get_visitor_by_id(data)
    if visitor:
        if not Activity.validate_postActivity(request.form):
            return redirect(request.referrer)
    if 'images' not in request.files:
        flash('Please upload an image', 'imagesPostActivity')
        return redirect(request.referrer)
    postActivityImages = request.files.getlist('images')
    imageAc_filenames = []
    for postAc_image in postActivityImages:
        if not allowed_file(postAc_image.filename):
            flash('The file should be in png, jpg or jpeg format!', 'imagesPostActivity')
            return redirect(request.referrer)
    
        if postAc_image:
            filename1 = secure_filename(postAc_image.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename1
            filename1 = time
            postAc_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            imageAc_filenames.append(filename1)
            
    imagePAct_string = ','.join(imageAc_filenames)
    data = {
        'comment': request.form['comment'],
        'images': imagePAct_string,
        'visitor_id': session['visitor_id'],
        'activity_id': id
    }
    Activity.addActivityPost(data)
    flash('Post created successfully', 'postActivitySuccessRegister')
    return redirect(request.referrer)

@app.route('/visitor/delete/postActivity/<int:id>')
def deletePostActivity(id):
    if 'visitor_id' not in session:
        return redirect('/visitor')
    data = {
        'id': id
    }
    postActivity = Activity.get_postActivity_by_id(data)
    
    if postActivity['visitor_id'] == session['visitor_id']:
        Activity.deleteActivityPost(data)
    return redirect(request.referrer)