from flask import Blueprint, make_response, redirect, render_template, request, flash, url_for
from website import views
from .models import Result, User
from . import db
from mailjet_rest import Client
from .env import mail_api_key, mail_api_secret, recipient_mail_id, sender_mail_id, path_wkhtmltopdf
import pdfkit


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('name')
        short_breadth = request.form.get('short_breadth')
        confusion = request.form.get('confusion')
        chest_pain = request.form.get('chest_pain')

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
        positivity_chance = "High"
    elif user.short_breadth == 'No' and user.confusion == 'No' and user.chest_pain == 'No':
        positivity_chance = "Low"
    else:
        positivity_chance = "Moderate"

    new_result = Result(positivity_chance=positivity_chance, userId=user.id)
    db.session.add(new_result)
    db.session.commit()

    flash('Result generated', category='success')

    send_mail(user, new_result)
    return render_template("result.html", user=user, result=new_result)


@views.route('/report/<user>/<result>')
def report(user, result):
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    rendered = render_template("report.html", user=user, result=result)
    pdf = pdfkit.from_string(
        rendered, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=CoviCheckerReport.pdf'
    return response


@views.route('/genreport', methods=['GET', 'POST'])
def genreport():
    if request.method == 'POST':
        user = request.form.get('user')
        result = request.form.get('result')
        return redirect(url_for('views.report', user=user, result=result))


def send_mail(user, new_result):
    api_key = mail_api_key
    api_secret = mail_api_secret
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": sender_mail_id,
                    "Name": "CoviChecker"
                },
                "To": [
                    {
                        "Email": recipient_mail_id,
                        "Name": "Admin"
                    }
                ],
                "Subject": "CoviChecker : New Data Submitted",
                "HTMLPart": "Dear Admin,<br />Name : {{ var:username }}<br />Positivity Chance : {{ var:userresult }}",
                "TemplateLanguage": True,
                "Variables": {"username": user.name, "userresult": new_result.positivity_chance}
            }
        ]
    }
    mailjet.send.create(data=data)
