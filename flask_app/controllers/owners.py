from flask_app import app
from flask import render_template, request, session, redirect, flash,jsonify, url_for
from flask_bcrypt import Bcrypt 
from flask_app.models.business import Business
from flask_app.models.owner import Owner


bcrypt = Bcrypt(app)
import paypalrestsdk
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

@app.route('/businessOwner')
def indexowner():
    if 'owner_id' in session:
        return redirect('/businessOwner/dashboard')
    return redirect('/logout')

@app.route('/loginPage/buisnessOwner')
def loginPageBusinessOwner():
    if 'owner_id' in session:
        return redirect('/businessOwner/dashboard')
    return render_template('businessOwnerLogin.html')


@app.route('/login/businessOwner', methods = ['POST'])
def loginowner():
    if 'owner_id' in session:
        return redirect('/businessOwner')
    if not Owner.validate_owner(request.form):
        return redirect(request.referrer)
    businessOwner = Owner.get_owner_by_email(request.form)
    if not businessOwner:
        flash('This email doesnt exist', 'ownerEmailLogin')
        return redirect(request.referrer)
    
    if not bcrypt.check_password_hash(businessOwner['password'], request.form['password']):
        flash('Incorrect password', 'ownerPasswordLogin')
        return redirect(request.referrer)
    
    session['owner_id']= businessOwner['id']
    return redirect('/businessOwner')

@app.route('/businessOwner/dashboard')
def dashboardOwner():
    if 'owner_id' not in session:
        return redirect('/businessOwner')
    data = {
        'id': session['owner_id']
    }
    owner=Owner.get_owner_by_id(data)
    businesses = Business.get_my_all_businesses(data)
    return render_template('businessOwnerdashboard.html', loggedOwner = owner, businesses=businesses)

@app.errorhandler(404) 
def invalid_route(e): 
    return render_template('404.html')

@app.route('/businessOwner/profile')
def businessOwnerProfile():
    if 'owner_id' not in session:
        return redirect('/businessOwner')
    data = {
        'id': session['owner_id']

    }
    
    loggedOwner = Owner.get_owner_by_id(data)
    return render_template('ownerProfile.html', loggedOwner = loggedOwner)

@app.route('/edit/owner')
def renterEditOwnerProfile():
    if 'owner_id' not in session:
        return redirect('/businessOwner')
    data = {
        'id': session['owner_id']
    }
    owner = Owner.get_owner_by_id(data)
    return render_template('ownerEditProfile.html', owner=owner)

@app.route('/update/owner', methods = ['POST'])
def updateOwnerProfile():
    if 'owner_id' not in session:
        return redirect('/businessOwner')
    data = {
        'id': session['owner_id']
        
    }
    owner = Owner.get_owner_by_id(data)
    if owner['id'] == session['owner_id']:
        if not Owner.validate_ownerUpdate(request.form):
            return redirect(request.referrer)
        data = {
            'email': request.form['email'],
            'phone': request.form['phone'],
            'id': session['owner_id']
        }
        Owner.update_owner(data)
        return redirect('/businessOwner/profile')
    return redirect('/businessOwner')

@app.route('/owner/business/new')
def newBusiness():
    if 'owner_id' not in session:
        return redirect('/businessOwner')
    data = {
        'id': session['owner_id']
    }
    return render_template('ownerNewBusiness.html',loggedOwner = Owner.get_owner_by_id(data))

@app.route('/owner/business/create', methods = ['POST'])
def addBusiness():
    if 'owner_id' not in session:
        return redirect('/businessOwner')
    data = {
        'id': session['owner_id']
    }
    owner = Owner.get_owner_by_id(data)
    if owner:
        if not Business.validate_business(request.form):
            return redirect(request.referrer)
    if 'images' not in request.files:
        flash('Please upload an image', 'imagesBusiness')
        return redirect(request.referrer)
    businessImages = request.files.getlist('images')
    image_filenames = []
    for business_image in businessImages:
        if not allowed_file(business_image.filename):
            flash('The file should be in png, jpg or jpeg format!', 'imagesBusiness')
            return redirect(request.referrer)
    
        if business_image:
            filename1 = secure_filename(business_image.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename1
            filename1 = time
            business_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            image_filenames.append(filename1)
            
    imageB_string = ','.join(image_filenames)
    data = {
        'name': request.form['name'],
        'type': request.form['type'],
        'description': request.form['description'],
        'email': request.form['email'],
        'phone': request.form['phone'],
        'address': request.form['address'],
        'images': imageB_string,
        'owner_id': session['owner_id']
    }
    Business.create_business(data)
    flash('Business created successfully', 'businessSuccessRegister')
    return redirect(request.referrer)

@app.route('/owner/business/<int:id>')
def oneBusiness(id):
    if 'owner_id' not in session:
        return redirect('/businessOwner')
    data = {
        'owner_id': session['owner_id'],
        'id': id
    }
    owner = Owner.get_owner_by_id(data)
    business = Business.get_business_by_id(data)
    return render_template('viewOneBusiness.html', owner=owner, business=business)
    

@app.route('/owner/business/edit/<int:id>')
def businessEdit(id):
    if 'owner_id' not in session:
        return redirect('/businessOwner')
    data = {
        'owner_id': session['owner_id'],
        'id': id
    }
    owner = Owner.get_owner_by_id(data)
    business = Business.get_business_by_id(data)
    return render_template('editBusiness.html', owner=owner, business=business)

@app.route('/owner/business/update/<int:id>', methods = ['POST'])
def updateBusiness(id):
    if 'owner_id' not in session:
        return redirect('/businessOwner')
    data = {
        'id': session['owner_id']
    }
    owner = Owner.get_owner_by_id(data)
    if owner:
        if not Business.validate_updateBusiness(request.form):
            return redirect(request.referrer)
    if 'images' not in request.files:
        flash('Please upload an image', 'imagesBusiness')
        return redirect(request.referrer)
    businessImages = request.files.getlist('images')
    image_filenames = []
    for business_image in businessImages:
        if not allowed_file(business_image.filename):
            flash('The file should be in png, jpg or jpeg format!', 'imagesBusiness')
            return redirect(request.referrer)
    
        if business_image:
            filename1 = secure_filename(business_image.filename)
            time = datetime.now().strftime("%d%m%Y%S%f")
            time += filename1
            filename1 = time
            business_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            image_filenames.append(filename1)
            
    imageB_string = ','.join(image_filenames)
    data = {
        'name': request.form['name'],
        'type': request.form['type'],
        'description': request.form['description'],
        'email': request.form['email'],
        'phone': request.form['phone'],
        'images': imageB_string,
        'owner_id': session['owner_id'],
        'id': id
    }
    Business.updateBusiness(data)
    flash('Business updated successfully', 'businessSuccessUpdated')
    return redirect(request.referrer)

@app.route('/make/payment')
def makePayment():
    if 'owner_id' not in session:
        return redirect('/businessOwner')
    data = {
        'id': session['owner_id']
    }
    owner=Owner.get_owner_by_id(data)
    
    return render_template('makePayment.html', loggedOwner = owner)


@app.route('/checkout/paypal')
def checkoutPaypal():
    if 'owner_id' not in session:
            return redirect('/businessOwner')
    cmimi = 10
    
    try:
        paypalrestsdk.configure({
            "mode": "sandbox", # Change this to "live" when you're ready to go live
            "client_id": "AdRJOyyK_pDYlXB6f_q70Gx-MvxqJuVQEBN8b0BEdqcHg3hhvBD7Nk0PV6GQ15tCgRk1zrl_gm8baBB2",
            "client_secret": "EKozGHz0v7yAVgFO3iy55DkmJkWxQs6_o2_sO32-_Q3EZDno2DwHM9NzIKBXlQGMsO8MKUfLziZZl3TQ"
        })

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": cmimi,
                    "currency": "USD"  # Adjust based on your currency
                },
                "description": f"Pagese per krijim biznesi."
            }],
            "redirect_urls": {
                "return_url": url_for('paymentSuccess', _external=True, cmimi=cmimi),
                "cancel_url": "http://example.com/cancel"
            }
        })

        if payment.create():
            approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
            return redirect(approval_url)
        else:
            flash('Something went wrong with your payment', 'creditCardDetails')
            return redirect(request.referrer)
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'creditCardDetails')
        return redirect(request.referrer)

@app.route("/success", methods=["GET"])
def paymentSuccess():
    payment_id = request.args.get('paymentId', '')
    payer_id = request.args.get('PayerID', '')
    try:
        paypalrestsdk.configure({
            "mode": "sandbox", # Change this to "live" when you're ready to go live
            "client_id": "AdRJOyyK_pDYlXB6f_q70Gx-MvxqJuVQEBN8b0BEdqcHg3hhvBD7Nk0PV6GQ15tCgRk1zrl_gm8baBB2",
            "client_secret": "EKozGHz0v7yAVgFO3iy55DkmJkWxQs6_o2_sO32-_Q3EZDno2DwHM9NzIKBXlQGMsO8MKUfLziZZl3TQ"
        })
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            
            
            ammount = request.args.get('cmimi')
            status = 'Paid'
            owner_id = session['owner_id']
            data = {
                'ammount': ammount,
                'status': status,
                'owner_id': owner_id
            }
            Owner.createPayment(data)
           
            flash('Your payment was successful!', 'paymentSuccessful')
            return redirect('/owner/business/new')
        else:
            flash('Something went wrong with your payment', 'paymentNotSuccessful')
            return redirect('/businessOwner')
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'paymentNotSuccessful')
        return redirect('/make/payment')


@app.route("/cancel", methods=["GET"])
def paymentCancel():
    flash('Payment was canceled', 'paymentCanceled')
    return redirect('/make/payment')

@app.route('/owner/delete/business/<int:id>')
def deleteBusiness(id):
    if 'owner_id' not in session:
        return redirect('/businessOwner')
    data = {
        'id': id,
    }
    business = Business.get_business_by_id(data)
    if business['owner_id'] == session['owner_id']:
        Business.deleteAllPostBusiness(data)
        Business.delete_business(data)
    return redirect('/businessOwner')