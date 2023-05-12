from flask import Blueprint, render_template,url_for,flash,redirect,request
from flask_login import login_required,current_user
from .model import *
import json

view = Blueprint('view', __name__)

@view.route('/')
def home_page():
    return render_template('home.html', user = current_user)

@view.route('/Dashboard', methods = ['GET','POST'])
@login_required
def dash():
    if current_user.is_authenticated and current_user.is_admin == False:
        vshows = Show.query.order_by(Show.date_added.desc())
        vvenues = Venue.query.order_by(Venue.id)
        vtags = Show.query.filter(Show.Tags)
        return render_template('Dashboard.html', user = current_user, vshows = vshows,vvenues = vvenues,vtags = vtags)
    else:
        flash("ADMIN CAN NOT ACCESS DASHBOARD")
        return redirect(url_for('admin.index'))
    
@view.route('/api/listvenue', methods = ["GET"])
def listvenue():
    vvenue = Venue.query
    venue = {}
    for v in vvenue:
        venue[v.id] = v.Name
    return {'api':list(venue.values())}

@view.route('/api/createvenue', methods = ["POST"])    
def createvenue():
    x = request.get_json()
    new_venue = Venue(Name = x["Name"], Place = x["Place"], Capacity = x["Capacity"])
    db.session.add(new_venue)
    db.session.commit()
    return ({"Response":"Venue Added"})


@view.route('/api/updatevenue', methods = ["PUT"])    
def updatevenue():
    x = request.get_json()
    update = Venue.query.filter_by(id = x["id"]).update(dict(Name = x["Name"],Place= x["Place"],Capacity = x["Capacity"]))
    db.session.commit()
    return ({"Response":"Venue Updated"})

@view.route('/api/deletevenue', methods = ["DELETE"])    
def deletevenue():
    x = request.get_json()
    venue = Venue.query.get(x["id"])
    db.session.delete(venue)
    db.session.commit()
    return ({"Response":"Venue Deleted"})

@view.route('/api/listshow',methods = ["GET"])
def listshow():
    vshows = Show.query
    show= {}
    for v in vshows:
        vvenue = Venue.query.filter(Venue.id == v.Venue_id).first()
        show[v.id] = v.Name,vvenue.Name
    return {'api':list(show.values())}

@view.route('/api/createshow', methods = ["POST"])    
def createshow():
    x = request.get_json()
    new_show = Show(Name = x["Name"], Ticket_price = float(x["Ticketprice"]),Tags = x['Tags'], startime = int(x["starttime"]), endtime = int(x["endtime"]), Venue_id = int(x["Venue_id"]))
    db.session.add(new_show)
    db.session.commit()
    return ({"Response":"Show Added"})

@view.route('/api/updateshow', methods = ["PUT"])    
def updateshow():
    x = request.get_json()
    update = Show.query.filter_by(id = x["id"]).update(dict(Name = x["Name"],Ticket_price = int(x["Ticketprice"]),Tags = x['Tags'],starttime = int(x["starttime"]), endtime = int(x["endtime"]),Venue_id = x["Venue_id"]))
    db.session.commit()
    return ({"Response":"Show Updated"})

@view.route('/api/deleteshow', methods = ["DELETE"])    
def deleteshow():
    x = request.get_json()
    show = Show.query.get(x["id"])
    db.session.delete(show)
    db.session.commit()
    return ({"Response":"Show Deleted"})