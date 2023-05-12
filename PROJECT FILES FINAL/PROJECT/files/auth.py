from flask import Blueprint, render_template,url_for,request,redirect,flash
from .model import *
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user,login_required,logout_user,current_user

auth = Blueprint('auth', __name__)

@auth.route('/login',methods = ['GET','POST'])
def login():  
    if request.method == "POST":
        vusername = request.form.get('Username')
        vpassword = request.form.get('typePasswordX')

        user = User.query.filter_by(username = vusername).first()
        if user:
            if check_password_hash(user.password,vpassword):
                flash('LOGGED IN')
                login_user(user)
                return redirect(url_for('view.dash'))
            else:
                flash('INCORRECT PASSWORD')
        else:
            flash('"USERNAME DOES NOT EXISTS"')
    return render_template('login.html')

@auth.route('/Adminlogin',methods = ['GET','POST'])
def Adminlogin(): 
    if request.method == "POST":
        vusername = request.form.get('Adminusername')
        vpassword = request.form.get('Adminpass')
        cadmin = User.query.filter_by(username = vusername).first()
        
        if cadmin:
            if check_password_hash(cadmin.password,vpassword) and cadmin.is_admin == True:
                flash('ADMIN LOGGED IN')
                login_user(cadmin)
                return redirect(url_for('admin.index'))
            else:
                flash('INCORRECT PASSWORD')
        else:
            flash('"ADMIN DOES NOT EXISTS"') 
    return render_template('Adminlogin.html')

@auth.route('/signup',methods = ['GET','POST'])
def signup():
    if request.method == 'POST':
        vusername = request.form.get('Username')
        vpassword = request.form.get('typePasswordX')

        user = User.query.filter_by(username = vusername).first()
        if user:
            flash('Username already exists', category = 'error')
        elif len(vpassword) < 3:
            flash('Password must be at least 3 characters.')
        else:
            new_user = User(username = vusername , password = generate_password_hash(vpassword, method = 'sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created', category = 'Success')
            return redirect(url_for('view.home_page'))
    return render_template("signup.html")

@auth.route('/Logout',methods = ['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('view.home_page'))



@auth.route('/show/<int:id>', methods=['GET' ,'POST'])
@login_required
def show(id):
    shows = Show.query.get_or_404(id)
    venue = Venue.query.get_or_404(shows.Venue_id)
    if request.method == "POST":   
        try:
            vbooking = int(request.form.get('booked')) #Int is enforced
            x = vbooking + shows.Booked
            if x <= venue.Capacity:
                new_booking = Bookings(Name = shows.Name,Tickets = vbooking,Ticket_price = (shows.Ticket_price+(shows.Rating*10)),Venue_id = venue.id , User_id = current_user.id)
                update = Show.query.filter_by(id = shows.id).update(dict(Booked = x))
                db.session.add(new_booking)
                db.session.commit()
                return redirect(url_for('auth.show',id = shows.id))
            else:
                flash("OUT OF SEATS")
                return redirect(url_for('view.dash'))
        except Exception as e:
            flash("ERROR " + str(e))
            return redirect(url_for('view.dash'))
    else:
        return render_template('show.html' , shows= shows, venue = venue) 


@auth.route('/profile/<int:id>', methods = ['POST','GET'])
@login_required
def profile(id):
    user = current_user
    vrating = request.form.get('rating')
    showname = request.form.get('showname')
    booking_id = request.form.get('bookingid')
    new_rating = Bookings.query.filter_by(id = booking_id).update(dict(Rating = vrating)) #updating seperate ratings in bookings
    cbookings = Bookings.query.filter(Bookings.Name == showname, Bookings.Rating > 0) #common bookings
    
    v_num = cbookings.count()
    if v_num == 0:
        v_num = 1
        new_rate = 0
        for b in cbookings:
            new_rate += b.Rating
        new_rate = new_rate/v_num
        updaterating =  Show.query.filter_by(Name = showname).update(dict(Rating = new_rate))
        db.session.commit()
        book = Bookings.query.filter_by(User_id = user.id)
        bookingscount = book.count()
        return render_template("profile.html",user = current_user, book = book,bookingscount=bookingscount)
    else:
        v_num = cbookings.count()
        new_rate = 0
        for b in cbookings:
            new_rate += b.Rating
        new_rate = new_rate/v_num
        updaterating =  Show.query.filter_by(Name = showname).update(dict(Rating = round(new_rate,1)))
        db.session.commit()
        book = Bookings.query.filter_by(User_id = user.id)
        bookingscount = book.count()
        return render_template("profile.html",user = current_user, book = book,bookingscount=bookingscount)
    

@auth.route('/search', methods=['GET','POST'])
@login_required
def search():
        vvenues = Venue.query.join(Show)
        vshows = Show.query.order_by(Show.date_added.desc())
        if request.method == 'POST':
            svenue = request.form.get('svenue')
            slocation= request.form.get('slocation')
            sshow=request.form.get('sshow')
            stags=request.form.get('stags')
            stime=request.form.get('stime')
            etime = request.form.get('etime')
            if len(svenue) != 0:
                vvenues= vvenues.filter(Venue.Name.like('%' + svenue + '%'))
            if len(slocation) != 0:
                vvenues= vvenues.filter(Venue.Place.like('%' + slocation + '%'))
            if len(sshow) != 0:
                vvenues= vvenues.filter(Show.Name.like('%' + sshow + '%'))
                vshows = vshows.filter(Show.Name.like('%' + sshow + '%'))
            if len(stags) != 0:
                vvenues= vvenues.filter(Show.Tags.like('%' + stags+ '%'))
                vshows = vshows.filter(Show.Tags.like('%' + stags + '%'))
            if len(stime) != 0:
                vvenues= vvenues.filter(Show.starttime >= stime)
                vshows = vshows.filter(Show.starttime >= stime)
            if len(stime) != 0 and len(etime) != 0:
                vvenues= vvenues.filter(Show.starttime >= stime,Show.starttime <= etime)
                vshows = vshows.filter(Show.starttime >= stime,Show.starttime <= etime)
            return render_template('search.html', vshows=vshows, vvenues = vvenues)
            
        else:
            return render_template('search.html', vshows=vshows, vvenues = vvenues)
            
            