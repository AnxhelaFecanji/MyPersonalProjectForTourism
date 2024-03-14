from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash

class Attraction:
    db_name = "tourismschema"
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.type = data['type']
        self.address = data['address']
        self.description = data['description']
        self.images = data.get('images', [])
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
    @classmethod
    def create_attraction(cls, data):
        query = "INSERT INTO attractions (name, type, address, description, images) VALUES (%(name)s, %(type)s, %(address)s, %(description)s, %(images)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_attractions(cls):
        query = "SELECT * FROM attractions;"
        results = connectToMySQL(cls.db_name).query_db(query)
        attractions = []
        if results:
            for attraction in results:
                attractions.append(attraction)
            return attractions
        return attractions
        
    @classmethod
    def get_attraction_by_id(cls, data):
        query = 'SELECT * FROM attractions where id = %(id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def get_posts_by_attraction_id(cls, data):
        query = 'SELECT * FROM postsAttractions LEFT JOIN visitors ON postsAttractions.visitor_id = visitors.id WHERE postsAttractions.attraction_id = %(id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        posts = []
        if results:
            for post in results:
                posts.append(post)
        return posts
    
    @classmethod
    def get_all_postsAttractions(cls):
        query = "SELECT * FROM postsAttractions LEFT JOIN visitors ON postsAttractions.visitor_id = visitors.id left join attractions On postsAttractions.attraction_id = attractions.id ;"
        results = connectToMySQL(cls.db_name).query_db(query)
        posts = []
        if results:
            for post in results:
                posts.append(post)
            return posts
        return posts
    
    @classmethod
    def delete_attraction(cls, data):
        query = "DELETE FROM attractions where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def update_attraction(cls, data):
        query = "UPDATE attractions SET  name=%(name)s, type=%(type)s, description = %(description)s, images = %(images)s where attractions.id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def addAttractionPost(cls, data):
        query = "INSERT INTO postsAttractions (comment, images, visitor_id, attraction_id) VALUES (%(comment)s, %(images)s, %(visitor_id)s, %(attraction_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_postAttraction_by_id(cls, data):
        query = 'SELECT * FROM postsAttractions where id = %(id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def deleteAllPostAttractions(cls, data):
        query = "DELETE FROM postsAttractions where postsAttractions.attraction_id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
   
    
    @classmethod
    def deleteAttractionPost(cls, data):
        query = "DELETE FROM postsAttractions where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @staticmethod
    def validate_attraction(attraction):
        is_valid = True
        if len(attraction['name'])<1:
            flash("Attraction is required!", 'nameAttraction')
            is_valid = False
        if len(attraction['type'])<1:
            flash("Type is required!", 'typeAttraction')
            is_valid = False
        if len(attraction['address'])<3:
            flash("Address is required!", 'addressAttraction')
            is_valid = False
        if len(attraction['description'])<3:
            flash("Description is required!", 'descriptioAttraction')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_updateAttraction(attraction):
        is_valid = True
        if len(attraction['name'])<1:
            flash("Attraction is required!", 'nameAttractionUpdate')
            is_valid = False
        if len(attraction['type'])<1:
            flash("Type is required!", 'typeAttractionUpdate')
            is_valid = False
        if len(attraction['description'])<3:
            flash("Description is required!", 'descriptioAttractionUpdate')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_postAttraction(post):
        is_valid = True
        if len(post['comment'])< 5:
            flash('comment should be more  or equal to 5 characters', 'postAttraction')
            is_valid = False
        return is_valid