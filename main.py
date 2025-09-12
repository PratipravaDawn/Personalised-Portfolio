import os
import smtplib
from datetime import timedelta
from functools import wraps
from flask import Flask, make_response, render_template, request, session, flash, redirect, url_for, send_file
from sqlalchemy import exists
from models import db, Store, Img
from utils import is_strong_password
from dotenv import load_dotenv
from report import generate_portfolio

load_dotenv()
MYMAIL = os.getenv("MYMAIL")
KEY = os.getenv("KEY")
SECRET = os.getenv("SECRET")

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///information.db'
app.config['SQLALCHEMY_BINDS'] = {
    'img': 'sqlite:///img.db'
}
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
app.secret_key = SECRET

db.init_app(app)


@app.before_request
def session_timeout():
    session.permanent = True
    session.modified = True


@app.route('/')
def home():
    return render_template('open.html')


@app.route('/<name>/')
def red(name):
    if name == 'login':
        return render_template('login.html')
    if name == 'signin':
        return render_template('signin.html')
    return redirect(url_for('home'))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('red', name='login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login/send', methods=["GET", "POST"])
def check():
    if request.method == "POST":
        username = request.form.get("uname")
        password = request.form.get("psw")
        with app.app_context():
            query = db.session.query(exists().where(Store.name == username))
        if query.scalar():
            with app.app_context():
                fish = db.session.execute(db.select(Store).where(Store.name == username)).scalar()
            if fish.key == password:
                session['user'] = username
                flash("Welcome!!! back sir")
                return redirect(url_for('dash'))

            else:
                flash("Wrong Password, Re-enter your credentials")
                return redirect(url_for('red', name='login'))
        else:
            error_msg = "You dont exist, please sign in "
            flash(error_msg)
            return redirect(url_for('red', name='signin'))


@app.route('/signin/send', methods=["GET", "POST"])
def give():

    if request.method == "POST":
        username = request.form.get("uname")
        password1 = request.form.get("psw1")
        password2 = request.form.get("psw2")
        email = request.form.get("email")

        if password1 != password2:
            error_msg = "The passwords don't match. Try again."
            flash(error_msg)
            return redirect(url_for('red', name='signin'))

        if not is_strong_password(password1):
            error_msg = "Password not strong enough"
            flash(error_msg)
            return redirect(url_for('red', name='signin'))

        with app.app_context():
            existing_user = db.session.query(Store).filter_by(mail=email).first()
            if existing_user:
                error_msg = "This user is already registered. Please log in."
                flash(error_msg)
                return redirect(url_for('red', name='login'))
            def_about = f"Hello I'm {username}!!!"
            def_pfp = "static/photos/Admin/default.jpg"

            new_user = Store(name=username, key=password1, mail=email, about=def_about, profile=def_pfp)
            db.session.add(new_user)
            db.session.commit()

        session['user'] = username
        flash("Welcome, new user!")
        return redirect(url_for('dash'))


@app.route('/forgot-password')
def forgot():
    return render_template('forgotpass.html')


@app.route('/forgot-password/transfer', methods=["POST"])
def email():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("username")

        with app.app_context():

            user = db.session.query(Store).filter_by(name=name).first()
        if user:
            if user.mail == email:
                try:
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(MYMAIL, KEY)
                    message = f"Subject: Password Recovery\n\nYour password is: {user.key}"
                    server.sendmail(MYMAIL, email, message)
                    server.quit()

                    msg = "The password has been sent to your email. Check the spam, if not found."
                    flash(msg)
                    return redirect(url_for('red', name='login'))

                except Exception as e:
                    error_msg = "Failed to send email. Please try again later."
                    flash(error_msg)
                    return redirect(url_for('forgot'))
            else:
                error_msg = "Username & Password doesnt match"
                flash(error_msg)
                return redirect(url_for('forgot'))
        else:
            error_msg = "You are a new user. Please Sign in."
            flash(error_msg)
            return redirect(url_for('red', name='signin'))


@app.route('/dashboard')
@login_required
def dash():
    image_query = False
    u = session['user']
    user = db.session.execute(db.select(Store).filter_by(name=u)).scalar()
    image_query = db.session.query(exists().where(Img.owner == u))
    if image_query:
        image_data = db.session.query(Img).filter_by(owner=u).all()
    response = make_response(render_template('dashboard.html', u=u, m=user.mail, a=user.about, p=user.profile, i=image_query, data=image_data))

    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

@app.route('/upload', methods=['POST'])
def pictures():
    u = session['user']
    if request.method == 'POST':
        tit = request.form.get("filename")
        des = request.form.get("desc")
        pict = request.files.get('pic')
        os.makedirs(f"static/photos/users/{u}", exist_ok=True)
        if pict:
            pict.save(os.path.join(f"static/photos/users/{u}/", pict.filename))
            path = os.path.join(f"static/photos/users/{u}/", pict.filename)

        project = Img(image_path=path, title=tit, description=des, owner=u)
        db.session.add(project)
        db.session.commit()
    return redirect(url_for('dash'))

@app.route('/edit_user', methods=['POST'])
def edit():
    u = session['user']
    ab = request.form.get("about")
    pfp = request.files.get('profile_img')

    os.makedirs(f"static/photos/users/{u}/profile", exist_ok=True)

    user = db.session.execute(db.select(Store).filter_by(name=u)).scalar()
    user.about = ab

    if pfp and pfp.filename != "":
        path = os.path.join(f"static/photos/users/{u}/profile", f"{u}.jpg")
        pfp.save(path)
        user.profile = path

    db.session.commit()
    return redirect(url_for('dash'))

@app.route('/delete/<int:id>')
def delete_image(id):
    image = db.session.execute(db.select(Img).filter_by(id=id)).scalar()
    if os.path.exists(image.image_path):
        os.remove(image.image_path)
    if image:
        db.session.delete(image)
        db.session.commit()
        flash('Image deleted.')
    return redirect(url_for('dash'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.clear()
    error_msg = "You have been logged out"
    flash(error_msg)
    return redirect(url_for('home'))

@app.route('/pdf')
def download_pdf():
    art = []
    u = session['user']
    user = db.session.execute(db.select(Store).filter_by(name=u)).scalar()
    image_query = db.session.query(exists().where(Img.owner == u))
    if image_query:
        image_data = db.session.query(Img).filter_by(owner=u).all()
    for image in image_data:
        art.append({
            "path": image.image_path,
            "title": image.title,
            "desc": image.description,
        })
    PDF = generate_portfolio(user=u, email=user.mail, about=user.about, profile_pic=user.profile, artworks=art)

    return send_file(PDF, as_attachment=True)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        db.create_all(bind_key="img")
    app.run(debug=True)
