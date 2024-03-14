from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash

class Business:
    db_name = "tourismschema"
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.type = data['type']
        self.description = data['description']
        self.email = data['email']
        self.phone = data['phone']
        self.address = data['address']
        self.images = data.get('images', [])
        self.owner_id = data['owner_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
    @classmethod
    def create_business(cls, data):
        query = "INSERT INTO businesses (name, type, description, email, phone, address, images, owner_id) VALUES (%(name)s, %(type)s, %(description)s, %(email)s, %(phone)s, %(address)s, %(images)s, %(owner_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_businesses(cls):
        query = "SELECT * FROM businesses;"
        results = connectToMySQL(cls.db_name).query_db(query)
        businesses = []
        if results:
            for business in results:
                businesses.append(business)
            return businesses
        return businesses
    
    @classmethod
    def get_my_all_businesses(cls, data):
        query = "SELECT * FROM businesses where owner_id = %(id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        businesses = []
        if results:
            for business in results:
                businesses.append(business)
            return businesses
        return businesses
    
    @classmethod
    def get_business_by_id(cls, data):
        query = 'SELECT * FROM businesses left join owners on businesses.owner_id = owners.id where businesses.id = %(id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def delete_business(cls, data):
        query = "DELETE FROM businesses where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def deleteComment(cls, data):
        query = "DELETE FROM comments where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def updateBusiness(cls, data):
        query = "UPDATE businesses SET name=%(name)s, type=%(type)s, description = %(description)s, email=%(email)s, phone=%(phone)s, images = %(images)s where businesses.id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def addBusinessPost(cls, data):
        query = "INSERT INTO postBusinesses (comment, images, visitor_id, business_id) VALUES (%(comment)s, %(images)s, %(visitor_id)s, %(business_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_postBusiness_by_id(cls, data):
        query = 'SELECT * FROM postBusinesses where id = %(id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def deleteAllPostBusiness(cls, data):
        query = "DELETE FROM postBusinesses where postBusinesses.business_id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def deleteBusinessPost(cls, data):
        query = "DELETE FROM postBusinesses where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_posts_by_activity_id(cls, data):
        query = 'SELECT * FROM postBusinesses LEFT JOIN visitors ON postBusinesses.visitor_id = visitors.id WHERE postBusinesses.business_id = %(id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        postsB = []
        if results:
            for post in results:
                postsB.append(post)
        return postsB
    
    @classmethod
    def get_all_postsBusinesses(cls):
        query = "SELECT * FROM postBusinesses LEFT JOIN visitors ON postBusinesses.visitor_id = visitors.id left join businesses ON postBusinesses.business_id = businesses.id ;"
        results = connectToMySQL(cls.db_name).query_db(query)
        posts = []
        if results:
            for post in results:
                posts.append(post)
            return posts
        return posts
    
    @staticmethod
    def validate_business(business):
        is_valid = True
        if len(business['name'])<1:
            flash("Name of business is required!", 'nameBusiness')
            is_valid = False
        if len(business['type'])<1:
            flash("Type of business is required!", 'typeBusiness')
            is_valid = False
        if len(business['description'])<3:
            flash(" Business description is required!", 'descriptionBusiness')
            is_valid = False
        if len(business['email'])<1:
            flash("Business email is required!", 'emailBusiness')
            is_valid = False
        if len(business['phone'])<1:
            flash("Business phone is required!", 'phoneBusiness')
            is_valid = False
        if len(business['address'])<3:
            flash("Address is required!", 'addressBusiness')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_updateBusiness(business):
        is_valid = True
        if len(business['name'])<1:
            flash("Name of business is required!", 'nameUpdateBusiness')
            is_valid = False
        if len(business['type'])<1:
            flash("Type of business is required!", 'typeUpdateBusiness')
            is_valid = False
        if len(business['description'])<3:
            flash(" Business description is required!", 'descriptionUpdateBusiness')
            is_valid = False
        if len(business['email'])<1:
            flash("Business email is required!", 'emailUpdateBusiness')
            is_valid = False
        if len(business['phone'])<1:
            flash("Business phone is required!", 'phoneUpdateBusiness')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_postBusiness(post):
        is_valid = True
        if len(post['comment'])< 5:
            flash('comment should be more  or equal to 5 characters', 'postBusiness')
            is_valid = False
        return is_valid