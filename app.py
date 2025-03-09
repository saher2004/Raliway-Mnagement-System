from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Aayaan%4010@localhost/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'd63134fa3eae50da45cc6ea3b5f24600'

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(3), primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'
    
class Admin(db.Model):
    __tablename__ = 'admin'
    name = db.Column(db.String(50),primary_key=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Ticket(db.Model):
    __tablename__ = "ticket"
    Ticket_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    train_name = db.Column(db.String(50), nullable=False)
    Phone_number = db.Column(db.Integer, nullable=False)
    t_date = db.Column(db.String(20), nullable=False)
    ticket_seat = db.Column(db.String(50), nullable=False)

class Train(db.Model):
    __tablename__ ="train"
    train_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    train_name =db.Column(db.String(100),nullable=False)
    arrival_time = db.Column(db.String(15),nullable=False)
    departure_time = db.Column(db.String(15),nullable=False)
    train_travel = db.Column(db.String(100),nullable=False)

class Train_status(db.Model):
    __tablename__ = "train_status"
    train_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    train_name =db.Column(db.String(100), nullable=False)
    booked_seat = db.Column(db.String(50), nullable=False)



@app.route('/')
def default():
    return render_template('login.html')


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        session['username'] = name  # Store username in session
        session['role'] = 'user'

        last_user = User.query.order_by(User.user_id.desc()).first()
        if last_user:
            new_id = f"{int(last_user.user_id) + 1:03d}"
        else:
            new_id = "001"
        new_user = User(user_id=new_id, name=name, email=email, password=password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Sign-up successful!', 'success')
            return redirect(url_for('home'))
        except IntegrityError:
            db.session.rollback()
            flash('Email already exists. Please use a different email.', 'danger')
            return redirect(url_for('sign_up'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('sign_up'))

    return render_template('sign_up.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        login_type = request.form['login_type']

        if login_type == 'User Login':
            user = User.query.filter_by(name=name).first()
            if user and user.password == password:
                session['username'] = name  # Store username in session
                session['role'] = 'user'  # Store role in session
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'danger')
                return redirect(url_for('login'))
            
        elif login_type == 'Admin Login':
            user = Admin.query.filter_by(name=name).first()
            if user and user.password == password:
                session['username'] = name
                session['role'] = 'admin'
                flash('Admin login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'danger')
                return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/home')
def home():
    if 'username' in session:
        if session['role'] == 'admin':
            return render_template('admin_home.html')
        else:
            return render_template('home.html')
    else:
        flash('Please log in first', 'warning')
        return redirect(url_for('login'))


@app.route('/buy_ticket', methods=['GET', 'POST'])
def buy_ticket():
    if request.method == "POST":
        name = request.form['fullName']
        train_name = request.form['t_name']
        Phone_number = request.form['phone']
        t_date = request.form['departureDate']
        email = request.form['email']
        ticket_seat = request.form['seat_no'] + "-" + request.form['Seating']

        last_ticket = Ticket.query.order_by(Ticket.Ticket_id.desc()).first()
        if last_ticket:
            new_id = f"{int(last_ticket.Ticket_id) + 1:03d}"
        else:
            new_id = "001"
        train_ = Train.query.filter_by(train_name=train_name).first()
        if train_:
            train_id = train_.train_id
            status = Train_status(train_id=train_id, train_name=train_name, booked_seat=ticket_seat)
            db.session.add(status)
            db.session.commit()

        new_ticket = Ticket(Ticket_id=new_id, name=name, email=email, train_name=train_name, Phone_number=Phone_number, t_date=t_date, ticket_seat=ticket_seat)
        try:
            db.session.add(new_ticket)
            db.session.commit()
            flash('Ticket booked successfully', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('buy_ticket'))
    return render_template('buy_ticket.html')


@app.route('/my_tickets', methods=['GET'])
def my_tickets():
    username = session.get('username')  # Get the username from session
    if username:
        all_tickets = Ticket.query.filter_by(name=username).all()
        return render_template('my_tickets.html', tickets=all_tickets)
    else:
        flash('You need to log in to view your tickets', 'danger')
        return redirect(url_for('login'))

@app.route('/train', methods=['GET'])
def train():
    trains = Train.query.all()
    return render_template('train.html',trains=trains)

@app.route('/train_status', methods=['GET'])
def train_status(): 
    trains = Train_status.query.all()
    return render_template('train_status.html', trains=trains)

@app.route('/ad_ticket', methods=['GET'])
def ad_ticket():
    tickets = Ticket.query.all()
    return render_template('admin_ticket.html', tickets=tickets)

@app.route('/ad_train', methods=['GET', 'POST'])
def ad_train():
    if request.method == 'POST':
        train_name = request.form['train_name']
        departure_time = request.form['departure_time']
        arrival_time = request.form['arrival_time']
        train_travel = request.form['train_travel']

        last_user = Train.query.order_by(Train.train_id.desc()).first()
        if last_user:
            train_id = f"{int(last_user.train_id) + 1}"
            
        else:
            train_id = int(1)

        new_train = Train(train_id=train_id, train_name=train_name, departure_time=departure_time, arrival_time=arrival_time, train_travel=train_travel)
        
        try:
            db.session.add(new_train)
            db.session.commit()
            flash('New train added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding train: {str(e)}', 'danger')

            
        return redirect(url_for('ad_train'))

        # Fetch existing train data for display
    trains = Train.query.all()
    return render_template('admin_train.html', trains=trains)




@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)