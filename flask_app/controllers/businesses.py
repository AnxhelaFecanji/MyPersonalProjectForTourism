from flask_app import app
from flask import render_template, redirect, flash, session, request, url_for
from flask_bcrypt import Bcrypt
from flask_app.models.business import Business
from flask_app.models.visitor import Visitor
from flask_app.models.owner import Owner


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
           
@app.route('/visitor/business/post/new/<int:id>')
def newpostBusiness(id):
    if 'visitor_id' not in session:
        return redirect('/visitor')
    data = {
        
        'id': id
        
    }
    business = Business.get_business_by_id(data)
    return render_template('visitorAddBusinessPost.html', business=business)
           


@app.route('/visitor/business/post/new/<int:id>', methods = ['POST'])
def createBusinessPost(id):
    if 'visitor_id' not in session:
        return redirect('/visitor')
    data = {
        'id': session['visitor_id']
    }
    visitor = Visitor.get_visitor_by_id(data)
    if visitor:
        if not Business.validate_postBusiness(request.form):
            return redirect(request.referrer)
    if 'images' not in request.files:
        flash('Please upload an image', 'imagesPostBusiness')
        return redirect(request.referrer)
    postBusinessImages = request.files.getlist('images')
    imageB_filenames = []
    for postB_image in postBusinessImages:
        if not allowed_file(postB_image.filename):
            flash('The file should be in png, jpg or jpeg format!', 'imagesPostBusiness')
            return redirect(request.referrer)
    
        if postB_image:
            filename1 = secure_filename(postB_image.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename1
            filename1 = time
            postB_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            imageB_filenames.append(filename1)
            
    imageB_string = ','.join(imageB_filenames)
    data = {
        'comment': request.form['comment'],
        'images': imageB_string,
        'visitor_id': session['visitor_id'],
        'business_id': id
    }
    Business.addBusinessPost(data)
    flash('Post created successfully', 'postBusinessSuccessRegister')
    return redirect(request.referrer)

@app.route('/visitor/delete/postBusiness/<int:id>')
def deletePostBusiness(id):
    if 'visitor_id' not in session:
        return redirect('/visitor')
    data = {
        'id': id
    }
    postBusiness = Business.get_postBusiness_by_id(data)
    
    if postBusiness['visitor_id'] == session['visitor_id']:
        Business.deleteBusinessPost(data)
    return redirect(request.referrer)

