from flask import Flask, render_template, request, jsonify, redirect, url_for, session,flash
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

db_config = {
    'dbname': 'sampledbs',
    'user': 'postgres',
    'password': 'abhix202',
    'host': 'localhost',
    'port': '5432'
}

def get_connection():
    return psycopg2.connect(
        dbname='sampledbs',
        user='postgres',
        password='abhix202',
        host='localhost',
        port='5432'
    )

def execute_query(query, values=None, fetch_all=False):
    with conn.cursor() as cursor:
        cursor.execute(query, values)
        if fetch_all:
            return cursor.fetchall()
        else:
            return cursor.fetchone()
@app.route('/')
def home():
    comments = get_comments()
    images = fetch_images_from_database()

    return render_template('index.html', images=images,comments=comments)
    
def execute_query(query, params=None, fetchall=False):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query, params)
        connection.commit()

        if fetchall:
            return cursor.fetchall()
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        query_check_username = "SELECT * FROM users WHERE username = %s;"
        result = execute_query(query_check_username, (username,))

        if result:
            return render_template('signup.html', message='Username already exists. Please sign in.')

        # If username is not taken, insert the new user
        query_insert_user = "INSERT INTO users (username, password) VALUES (%s, %s);"
        execute_query(query_insert_user, (username, password))

        return 'User signed up successfully!'

    return render_template('signup.html', message=None)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = "SELECT * FROM users WHERE username = %s AND password = %s;"
        user = execute_query(query, (username, password), fetchall=True)

        if user:
            session['username'] = username  
            return redirect(url_for('home'))
        else:
            return 'Invalid credentials. Please try again.'

    return render_template('signin.html')

@app.route('/signout')
def signout():
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('home'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')

    search_query = f"SELECT * FROM users WHERE username ILIKE %s;"
    results = execute_query(search_query, (f'%{query}%',), fetchall=True)

    users = [{'id': user[0], 'username': user[0]} for user in results]

    return jsonify({'users': users})

@app.route('/add_comment', methods=['POST'])
def add_comment():
    username = session.get('username')
    print(username)
    comment_text = request.form['comment_text']
    
    if username and comment_text:
        insert_comment(username, comment_text)
    else:
        print("error commenting")
        flash('Please log in to add a comment.', 'error')

    return redirect(url_for('home'))

def get_comments():
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute('SELECT * FROM comments')
    comments = cur.fetchall()
    conn.close()
    return comments

def insert_comment(username, comment_text):
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute('INSERT INTO comments (username, comment_text) VALUES (%s, %s)', (username, comment_text))
    conn.commit()
    conn.close()

def fetch_images_from_database():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT image_url, image_name, image_description FROM images;')
    images = cur.fetchall()
    conn.close()
    return images

if __name__ == '__main__':
    app.run(debug=True)
