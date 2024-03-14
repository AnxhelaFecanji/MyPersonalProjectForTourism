from flask_app import app
from flask import render_template, redirect, flash, session, request, url_for
from flask_bcrypt import Bcrypt

from flask_app.models.admin import Admin
from flask_app.models.owner import Owner
from flask_app.models.attraction import Attraction
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
           
@app.route('/visitor/attraction/post/new/<int:id>')
def newpostAttraction(id):
    if 'visitor_id' not in session:
        return redirect('/visitor')
    data = {
        
        'id': id
        
    }
    attraction = Attraction.get_attraction_by_id(data)
    return render_template('visitorAddAttractionPost.html', attraction=attraction)
           


@app.route('/visitor/attraction/post/new/<int:id>', methods = ['POST'])
def createAttractionPost(id):
    if 'visitor_id' not in session:
        return redirect('/visitor')
    data = {
        'id': session['visitor_id']
    }
    visitor = Visitor.get_visitor_by_id(data)
    if visitor:
        if not Attraction.validate_postAttraction(request.form):
            return redirect(request.referrer)
    if 'images' not in request.files:
        flash('Please upload an image', 'imagesPostAttraction')
        return redirect(request.referrer)
    postAttractionImages = request.files.getlist('images')
    image_filenames = []
    for post_image in postAttractionImages:
        if not allowed_file(post_image.filename):
            flash('The file should be in png, jpg or jpeg format!', 'imagesPostAttraction')
            return redirect(request.referrer)
    
        if post_image:
            filename1 = secure_filename(post_image.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename1
            filename1 = time
            post_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            image_filenames.append(filename1)
            
    imagePAtt_string = ','.join(image_filenames)
    data = {
        'comment': request.form['comment'],
        'images': imagePAtt_string,
        'visitor_id': session['visitor_id'],
        'attraction_id': id
    }
    Attraction.addAttractionPost(data)
    flash('Post created successfully', 'postAttractionSuccessRegister')
    return redirect(request.referrer)

@app.route('/visitor/delete/post/<int:id>')
def deleteComment(id):
    if 'visitor_id' not in session:
        return redirect('/visitor')
    data = {
        'id': id
    }
    post = Attraction.get_postAttraction_by_id(data)
    
    if post['visitor_id'] == session['visitor_id']:
        Attraction.deleteAttractionPost(data)
    return redirect(request.referrer)