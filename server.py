from flask_app import app

from flask_app.controllers import admin, owners, attractions,visitors, activities, businesses

if __name__=="__main__":     
    app.run(debug=True)  