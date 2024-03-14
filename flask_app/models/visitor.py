from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
PASWORD_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
class Visitor:
    db_name = "tourismschema"
    def __init__(self, data):
        self.id = data['id']
        self.firstName = data['firstName']
        self.lastName = data['lastName']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
    @classmethod
    def get_all_visitors(cls):
        query = "SELECT * FROM visitors;"
        results = connectToMySQL(cls.db_name).query_db(query)
        visitors = []
        if results:
            for row in results:
                visitors.append(row)
        return visitors

    @classmethod
    def get_visitor_by_email(cls, data):
        query = 'SELECT * FROM visitors where email = %(email)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def get_visitor_by_id(cls, data):
        query = 'SELECT * FROM visitors where id = %(id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
        
    
    @classmethod
    def create_visitor(cls, data):
        query = "INSERT INTO visitors (firstName, lastName, email, password) VALUES (%(firstName)s, %(lastName)s, %(email)s, %(password)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def update_visitor(cls, data):
        query = "UPDATE visitors SET email = %(email)s WHERE visitors.id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    
    @staticmethod
    def validate_visitor(visitor):
        is_valid = True
        if not EMAIL_REGEX.match(visitor['email']): 
            flash("Invalid email address!", 'visitorEmailLogin')
            is_valid = False
        if len(visitor['password'])<8:
            flash("Password is required!", 'visitorPasswordLogin')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_visitorRegister(visitor):
        is_valid = True
        if not EMAIL_REGEX.match(visitor['email']): 
            flash("Invalid email address!", 'visitorEmailRegister')
            is_valid = False
        if len(visitor['password'])<8:
            flash("Password should be minimum 8 characters!", 'visitorPasswordRegister')
            is_valid = False 
 
        if len(visitor['confirm_password'])<8:
            flash("Confirm Password should be minimum 8 characters!", 'visitorConfirmPasswordRegister')
            is_valid = False  
        if visitor['password'] != visitor['confirm_password']:
            flash("Your password is different from the confirmed password ", 'errorvisitorPasswordRegister')   
            is_valid = False 
        if len(visitor['firstName'])<1:
            flash("First name is required!", 'visitorNameRegister')
            is_valid = False
        if len(visitor['lastName'])<1:
            flash("Last name is required!", 'visitorlastNameRegister')  
        return is_valid
    
    @staticmethod
    def validate_visitorUpdate(visitor):
        is_valid = True
        if not EMAIL_REGEX.match(visitor['email']): 
            flash("Invalid email address!", 'visitorEmailUpdate')
            is_valid = False
        return is_valid