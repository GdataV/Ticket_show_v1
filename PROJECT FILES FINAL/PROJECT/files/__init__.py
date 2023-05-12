from flask import Flask,request,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_admin import Admin, AdminIndexView,expose,BaseView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
import json

db = SQLAlchemy()
db_name = 'showapp.db'

def create_app():
    app = Flask(__name__)
    app.secret_key = 'sk'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}'
    db.init_app(app)
    
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from .view import view as view_blueprint
    app.register_blueprint(view_blueprint)

    from .model import User,Show,Venue
    
    class securemodelview(ModelView):
        column_display_pk = True
        def is_accessible(self):
            if current_user.is_authenticated and current_user.is_admin == True:
                return True
        def inaccessible_callback(self, name, **kwargs):
            flash("YOU ARE NOT AN ADMIN")
            return redirect(url_for('view.home_page', next=request.url))
    
    
    class showmodelview(ModelView):
        column_hide_backrefs = False
        column_display_pk = True
        column_auto_select_related = True
        form_columns = ( 'Name', 'Tags', 'Ticket_price', 'Venue_id', 'starttime' ,'endtime')
        def is_accessible(self):
            if current_user.is_authenticated and current_user.is_admin == True:
                return True
        def inaccessible_callback(self, name, **kwargs):
            flash("YOU ARE NOT AN ADMIN")
            return redirect(url_for('view.home_page', next=request.url))
    
    class indexview(AdminIndexView):
        def is_accessible(self):
            if current_user.is_authenticated and current_user.is_admin == True:
                return True
        def inaccessible_callback(self, name, **kwargs):
            flash("YOU ARE NOT AN ADMIN")
            return redirect(url_for('view.home_page', next=request.url))
    
    class summaryview(BaseView):
        @expose('/')
        def index(self):
            shows = Show.query.all()
            sold = []
            showname = []
            for i in shows:
                showname.append(i.Name)
                sold.append(i.Booked)
            return self.render('admin/summary.html', shows = shows,data1=json.dumps(showname), data2=json.dumps(sold))
    
    
    admin = Admin(app,index_view = indexview(),template_mode='bootstrap3')  
    admin.add_view(securemodelview(User,db.session))
    admin.add_view(showmodelview(Show,db.session))
    admin.add_view(securemodelview(Venue,db.session))
    admin.add_view(summaryview(name = 'Summary', endpoint = 'summary'))

    
    
    create_database(app)



    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app

def create_database(app):
    if not path.exists('files/' + db_name):
        with app.app_context():
            db.create_all()
           
            
