from flask import Blueprint, render_template, request, flash, redirect, url_for
from website import views
from .models import Result, User
from . import db

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('name')
        short_breadth = request.form.get('short_breadth')
        confusion = request.form.get('confusion')
        chest_pain = request.form.get('chest_pain')
        print(name, short_breadth, confusion, chest_pain)

        if len(name) == 0:
            flash('Name cannot be empty', category='error')
        elif not (short_breadth and confusion and chest_pain):
            flash('Please answer all the questions', category='error')
        else:
            new_user = User(name=name, short_breadth=short_breadth, confusion=confusion,
                            chest_pain=chest_pain)
            db.session.add(new_user)
            db.session.commit()
            flash('Data submitted successfully', category='primary')
            return result(new_user)

    return render_template("home.html")


@views.route('/result', methods=['GET', 'POST'])
def result(user):
    if user.short_breadth == 'Yes' and user.confusion == 'Yes' and user.chest_pain == 'Yes':
        positivityChance = "High"
    elif user.short_breadth == 'No' and user.confusion == 'No' and user.chest_pain == 'No':
        positivityChance = "Low"
    else:
        positivityChance = "Moderate"

    new_result = Result(positivityChance=positivityChance, userId=user.id)
    db.session.add(new_result)
    db.session.commit()
    flash('Result generated', category='success')
    return render_template("result.html", user=user, result=new_result)
