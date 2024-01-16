from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
import sqlite3
from flask import session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

from flask_sqlalchemy import SQLAlchemy

def create_connection():
    return sqlite3.connect('users.db')

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT NOT NULL,
            soyad TEXT NOT NULL,
            email TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            country TEXT NOT NULL,
            city TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

create_table()
def create_connection():
    conn = sqlite3.connect('users.db')
    return conn

def store_user_in_database(ad, soyad, email, username, password, country, city):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (ad, soyad, email, username, password, country, city)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ad, soyad, email, username, password, country, city))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error storing user in the database: {str(e)}")

@app.route('/register', methods=['POST'])
def register():
    try:
        ad = request.form['ad']
        soyad = request.form['soyad']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        country = request.form['country']
        city = request.form['city']

        store_user_in_database(ad, soyad, email, username, password, country, city)

        # Render the indexUser.html page with the welcome message
        return render_template('indexUser.html', username=username)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


def initialize_database():
    conn = sqlite3.connect('product_details.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_details (
            id INTEGER PRIMARY KEY,
            product_id TEXT,
            product_no TEXT,
            transmission TEXT,
            image_url TEXT,
            deposit REAL,
            mileage REAL,
            age TEXT,
            rental_cost REAL,
            rentalDays REAL,
            FOREIGN KEY(product_id) REFERENCES product_details(id)          
        )
    ''')
    cursor.execute('DELETE FROM product_details')

    product_details_data = [
        ('EKONOMİK','Renault Clio' ,'Manuel','https://www.avis.com.tr/Avis/media/Avis/Cars/b-renault-clio.png' ,2500, 1500, '21 Yaş Ve Üstü', 3195,1),
        ('KONFOR', 'Peugeot 2008','Otomatik','https://www.avis.com.tr/Avis/media/Avis/Cars/p-peugeot-2008.png',3000 , 1500, '23 Yaş Ve Üstü', 5090,1),
        ('PRESTİJ', 'Volkswagen Passat Variant','Otomatik','https://www.avis.com.tr/Avis/media/Avis/Cars/j-volkswagen-passat-variant.png', 3500 , 1500, '25 Yaş Ve Üstü', 7306,1)
    ]

    for details in product_details_data:
        cursor.execute('''
            INSERT INTO product_details (product_id, product_no, transmission, image_url, deposit, mileage, age, rental_cost,rentalDays)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', details)

    conn.commit()
    conn.close()


# Ana sayfa
@app.route('/')
def index():
    initialize_database()
    return render_template('index.html')

def calculateRentalCost(rentalDay):
    conn = sqlite3.connect('product_details.db')
    conn.connect('product_details.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE product_details SET rentalDays = rental_cost * 2')



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            error = 'Username and password are required.'
            return render_template('login.html', error=error)

        # Connect to the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))  
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template('login.html')



@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login')) 

    return render_template('indexUser.html')



def is_logged_in():
    return 'username' in session
    
@app.route('/indexUser')
def index_user():
    username = session.get('username','city', None)

    if username:
        return render_template('indexUser.html', username=username)
    else:
        return redirect(url_for('register_form'))
    

@app.route('/user_register', methods=['POST'])
def user_register():
    selected_city = request.form.get('city')
    return render_template('indexUser.html', selected_city=selected_city)

@app.route('/get_username')
def get_username():
    # Assuming you have a function to get the username from the database
    username = get_username_from_database()  # You need to implement this function

    if username:
        return jsonify({'success': True, 'username': username})
    else:
        return jsonify({'success': False, 'message': 'Error getting username from the database'})

def get_username_from_database():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users ORDER BY id DESC LIMIT 1')  
        username = cursor.fetchone()[0]  
        conn.close()
        return username
    except Exception as e:
        print(f"Error retrieving username from the database: {str(e)}")
        return None

@app.route('/login-page')
def login_page():
    return render_template('login.html')

@app.route('/register-page')
def register_page():
    return render_template('register.html')

@app.route('/indexUser-page')
def indexUser_page():
    return render_template('indexUser.html')

@app.route('/search', methods=['GET'])
def search():
    conn = sqlite3.connect('product_details.db')  
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM product_details') 
    products = cursor.fetchall()
    conn.close()

    rental_days = int(request.args.get('rentalDays', 0))

    return render_template('search.html', products=products, rentalDays=rental_days)


app.secret_key = 'your_secret_key' 


@app.route('/update_map', methods=['GET'])
def update_map():
    selected_city = request.args.get('city')

    city_coordinates = get_city_coordinates(selected_city)

    return jsonify(city_coordinates)

def get_city_coordinates(city):
  
    coordinates = {
        'Ankara': {'latitude': 39.9334, 'longitude': 32.8597},
        'İstanbul': {'latitude': 41.0082, 'longitude': 28.9784},
        'İzmir': {'latitude': 38.4192, 'longitude': 27.1287},
        'New York': {'latitude': 40.7128, 'longitude': -74.0060},
        'Los Angeles': {'latitude': 34.0522, 'longitude': -118.2437},
        'Chicago': {'latitude': 41.8781, 'longitude': -87.6298},
        'Roma': {'latitude': 41.9028, 'longitude': 12.4964},
        'Milano': {'latitude': 45.4642, 'longitude': 9.1900},
        'Napoli': {'latitude': 40.8522, 'longitude': 14.2681},
    }

    return coordinates.get(city, {'latitude': 0.0, 'longitude': 0.0})


@app.route('/auth/google')
def google_login():
  
    return render_template('indexUser.html')

if __name__ == '__main__':
    app.run(debug=True)
