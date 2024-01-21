from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_flavor.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)

# Item model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)
    availability = db.Column(db.Boolean, default=True)
    user_preferences = db.Column(db.String(255))
    ratings = db.relationship('Rating', backref='item', lazy=True)

# Rating model
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    items = Item.query.all()
    return render_template('index.html', items=items)

@app.route('/add_item', methods=['POST'])
@login_required
def add_item():
    item_name = request.form.get('item_name')
    location = request.form.get('location')
    item_type = request.form.get('item_type')
    availability = request.form.get('availability')
    user_preferences = request.form.get('user_preferences')

    if item_name and location and item_type and availability is not None:
        new_item = Item(item_name=item_name, user_name=current_user.username, location=location, user_id=current_user.id,
                        item_type=item_type, availability=bool(availability), user_preferences=user_preferences)
        db.session.add(new_item)
        db.session.commit()
        flash('Item added successfully!', 'success')
    else:
        flash('Item addition failed. Please provide all required information.', 'error')

    return redirect(url_for('index'))

@app.route('/rate_item/<int:item_id>/<int:stars>')
@login_required
def rate_item(item_id, stars):
    item = Item.query.get(item_id)
    if item:
        new_rating = Rating(stars=stars, item_id=item_id)
        db.session.add(new_rating)
        db.session.commit()

    return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    # Handle user registration logic here
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username and password:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
    else:
        flash('Registration failed. Please provide a username and password.', 'error')

    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login failed. Please check your username and password.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
