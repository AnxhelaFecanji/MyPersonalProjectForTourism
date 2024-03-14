from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash

class Activity:
    db_name = "tourismschema"
    def __init__(self, data):
        self.id = data['id']
        self.activity = data['activity']
        self.activityDate = data['activityDate']
        self.duration = data['duration']
        self.location = data['location']
        self.description = data['description']
        self.images = data.get('images', [])
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
    @classmethod
    def create_activity(cls, data):
        query = "INSERT INTO activities (activity, activityDate, duration, location, description, images) VALUES (%(activity)s, %(activityDate)s, %(duration)s, %(location)s, %(description)s, %(images)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_activities(cls):
        query = "SELECT * FROM activities;"
        results = connectToMySQL(cls.db_name).query_db(query)
        activities = []
        if results:
            for activity in results:
                activities.append(activity)
            return activities
        return activities
        
    @classmethod
    def get_activity_by_id(cls, data):
        query = 'SELECT * FROM activities where id = %(id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def delete_activity(cls, data):
        query = "DELETE FROM activities where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def update_activity(cls, data):
        query = "UPDATE activities SET  activity=%(activity)s, activityDate=%(activityDate)s, duration=%(duration)s, location=%(location)s, description = %(description)s, images = %(images)s where activities.id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def addActivityPost(cls, data):
        query = "INSERT INTO postsActivities (comment, images, visitor_id, activity_id) VALUES (%(comment)s, %(images)s, %(visitor_id)s, %(activity_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_postActivity_by_id(cls, data):
        query = 'SELECT * FROM postsActivities where id = %(id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def deleteAllPostActivity(cls, data):
        query = "DELETE FROM postsActivities where postsActivities.activity_id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def deleteActivityPost(cls, data):
        query = "DELETE FROM postsActivities where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_posts_by_activity_id(cls, data):
        query = 'SELECT * FROM postsActivities LEFT JOIN visitors ON postsActivities.visitor_id = visitors.id WHERE postsActivities.activity_id = %(id)s;'
        results = connectToMySQL(cls.db_name).query_db(query, data)
        posts = []
        if results:
            for post in results:
                posts.append(post)
        return posts
    
    @classmethod
    def get_all_postsActivities(cls):
        query = "SELECT * FROM postsActivities LEFT JOIN visitors ON postsActivities.visitor_id = visitors.id left join activities On postsActivities.activity_id = activities.id ;"
        results = connectToMySQL(cls.db_name).query_db(query)
        posts = []
        if results:
            for post in results:
                posts.append(post)
            return posts
        return posts
    
    @staticmethod
    def validate_activity(activity):
        is_valid = True
        if len(activity['activity'])<3:
            flash("Activity is required!", 'nameActivity')
            is_valid = False
        if len(activity['activityDate'])<1:
            flash("Date of activity is required!", 'dateActivity')
            is_valid = False
        if len(activity['duration'])<1:
            flash("Duration of activity is required!", 'durationActivity')
            is_valid = False
        if len(activity['location'])<1:
            flash("Location of activity is required!", 'locationActivity')
            is_valid = False
        if len(activity['description'])<3:
            flash("Description is required!", 'descriptioActivity')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_updateActivity(activity):
        is_valid = True
        if len(activity['activity'])<3:
            flash("Activity is required!", 'nameActivityUpdate')
            is_valid = False
        if len(activity['activityDate'])<1:
            flash("Date of activity is required!", 'dateActivityUpdate')
            is_valid = False
        if len(activity['duration'])<1:
            flash("Duration of activity is required!", 'durationActivityUpdate')
            is_valid = False
        if len(activity['location'])<1:
            flash("Location of activity is required!", 'locationActivityUpdate')
            is_valid = False
        if len(activity['description'])<3:
            flash("Description is required!", 'descriptioActivityUpdate')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_postActivity(post):
        is_valid = True
        if len(post['comment'])< 5:
            flash('comment should be more  or equal to 5 characters', 'postActivity')
            is_valid = False
        return is_valid