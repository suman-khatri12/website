from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_required, current_user, logout_user, UserMixin, LoginManager
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hellosecretkey'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/licence"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


db = SQLAlchemy(app)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), nullable=False)
    middlename = db.Column(db.String(80), nullable=True)
    lastname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.NUMERIC(10), unique=True, nullable=False)
    forms = db.relationship('Taxform', backref='user')

    def __repr__(self):
        return f'{self.name} and {self.email}'


class Taxform(db.Model):
    form_id = db.Column(db.Integer, primary_key=True)
    vehiclecc = db.Column(db.NUMERIC(5), nullable=False)
    vehicle_no = db.Column(db.VARCHAR(40), nullable= False, unique=True)
    company = db.Column(db.String(180))
    zone = db.Column(db.String(40))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


@app.route('/')
def home():
    return render_template('index.html', user=current_user)


@app.route('/rules')
def index():
    return render_template('rules.html')


@app.route('/rates')
def rates():
    return render_template('rate.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        fname = request.form['fname']
        mname = request.form['mname']
        lname = request.form['lname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        phoneno = Users.query.filter_by(phone=phone).first()
        if phoneno:
            flash('Phone number already exists')
            return redirect('/register')
        else:
            user = Users(firstname=fname, middlename=mname, lastname=lname, email=email, password=password, phone=phone)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')

    else:
        return render_template('registration.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        phone = request.form['pnum']
        password = request.form['password']

        phoneno = Users.query.filter_by(phone=phone).first()
        my_pass = Users.query.filter_by(password=password).first()

        if not phoneno and not my_pass:
            flash('Login details not matched!')
            return redirect('/login')
        login_user(phoneno)
        return redirect('/')
    else:
        return render_template('login.html')


@app.route('/form/<int:id>', methods=['POST', 'GET'])
@login_required
def form(id):
    if request.method == 'POST':
        zone = request.form['zone']
        v_no = request.form['v_no']
        company = request.form['company']
        cc = request.form['cc']
        bike_cc = int(cc)
        user = Users.query.filter_by(id=id).first()
        tax = Taxform(vehiclecc=cc, company=company,zone = zone, vehicle_no =v_no ,user_id=id)
        db.session.add(tax)
        db.session.commit()
        if bike_cc <= 125:
            cost = 3000
        if bike_cc > 125 and bike_cc <= 150:
            cost = 4500
        if bike_cc > 150 and bike_cc <= 225:
            cost = 6500
        if bike_cc > 225 and bike_cc <= 400:
            cost = 11000
        if bike_cc > 400 and bike_cc <= 650:
            cost = 20000
        if bike_cc > 650:
            cost = 30000
        return render_template('payment.html', total=cost, user=user, bill_detail=tax,)
    else:
        user_id = Users.query.filter_by(id=id).first()
        return render_template('form.html', user=user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


if __name__ == '__main__':
    app.run()
