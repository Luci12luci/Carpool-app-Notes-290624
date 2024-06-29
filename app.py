from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://uwj8p4v8zuoeyv3iqlxg:Kh3N5D3JtxcCyJeXuUeeZVNCROL6Jo@b1mxnbtfaytwhs4af34m-postgresql.services.clever-cloud.com:50013/b1mxnbtfaytwhs4af34m"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Pripojenie k PostgreSQL databáze
# conn = psycopg2.connect(
#     dbname='b1mxnbtfaytwhs4af34m',
#     user='uwj8p4v8zuoeyv3iqlxg',
#     password='Kh3N5D3JtxcCyJeXuUeeZVNCROL6Jo',
#     host="b1mxnbtfaytwhs4af34m-postgresql.services.clever-cloud.com",
#     port=50013
# )

class Rides(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)


users = {
    'john': 'password123',
    'jane': 'mypassword'
}


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            return redirect(url_for('welcome', username=username))
        else:
            error = "Invalid username or password"
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/welcome/<username>')
def welcome(username):
    return render_template('welcome.html', username=username)


# Ďalšie routy a funkcie (registrácia, prihlásenie, vytváranie ciest, atď.)

# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         # Implementujte pridanie používateľa do databázy
#         # Napríklad:
#         cur = conn.cursor()
#         cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
#         conn.commit()
#         cur.close()
#         return redirect(url_for("login"))  # Presmerovanie na prihlásenie
#     return render_template("register.html")


# @app.route("/create_ad", methods=["GET", "POST"])
# def create_ad():
#     if request.method == "POST":
#         from_location = request.form["from_location"]
#         to_location = request.form["to_location"]
#         date = request.form["date"]
#         notes = request.form["notes"]
#         cur = conn.cursor()
#         cur.execute("INSERT INTO rides (from_location, to_location, date, notes) VALUES (%s, %s, %s, %s)",
#                     (from_location, to_location, date, notes))
#         conn.commit()
#         cur.close()
#         return redirect(url_for("success"))
#     else:
#         return render_template("create_ad.html")

@app.route('/create_ad', methods=['GET', 'POST'])
def create_ad():
    if request.method == 'POST':
       from_location = request.form['from_location']
       to_location = request.form['to_location']
       date = request.form['date']
       notes = request.form['notes']

       try:
           ride = Rides(from_location=from_location, to_location=to_location, date=date, notes=notes)
           db.session.add(ride)
           db.session.commit()
           return redirect('/success')
       except Exception as e:
            print(f"Error inserting data: {str(e)}")
            return "An error occurred while inserting data. Please try again."

    return render_template('create_ad.html')

@app.route('/success')
def success():
    return 'Inzerát bol úspešne vytvorený!'


# @app.route("/search")
# def search():
#     # Získanie údajov o cestách z databázy na základe vyhľadávania
#     if request.method == 'POST':
#      from_location = request.form.get('from_location')
#      to_location = request.form.get('to_location')
#      filtered_rides = [ride for ride in rides if
#                       from_location.lower() in ride['from_location'].lower() and
#                       to_location.lower() in ride['to_location'].lower()]
#      cur = conn.cursor()
#      cur.execute("SELECT * FROM trips WHERE route ILIKE %s", (f"%{search_term}%",))
#      trips = cur.fetchall()
#      cur.close()
#      return render_template('search.html', rides=filtered_rides)
# return render_template('search.html', rides=rides)


# @app.route("/search", methods=['GET', 'POST'])
# def search():
#     rides = request.args.get("rides")
#     if request.method == 'POST':
#         from_location = request.form.get('from_location')
#         to_location = request.form.get('to_location')
#         filtered_rides = [ride for ride in rides if
#                           from_location.lower() in ride['from_location'].lower() and
#                           to_location.lower() in ride['to_location'].lower()]
#     # Implementujte logiku pre vyhľadávanie ciest v databáze na základe zadaných kritérií
#     # Napríklad: SELECT * FROM trips WHERE route ILIKE %s;
#     # ILIKE umožňuje nezávislé na veľkosti písmen vyhľadávanie
#     cur = conn.cursor()
#     cur.execute("SELECT from_location, to_location, date FROM rides WHERE from_location ILIKE %s",
#                 (f"%{rides}%",))
#     rides = cur.fetchall()
#     cur.close()
#     return render_template("search.html", rides=rides)


@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        from_location = request.form.get('from_location')
        to_location = request.form.get('to_location')

        try:
            rides = Rides.query.filter(Rides.from_location.ilike(f"%{from_location}%")).all()

            if rides:
                filtered_rides = [ride for ride in rides if ride.to_location.lower() == to_location.lower()]
            else:
                filtered_rides = []  # No rides found

            if not filtered_rides:
                return "No rides found."  # Display a message when no rides match the criteria

            return render_template("search.html", rides=filtered_rides)
        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("search.html")


if __name__ == '__main__':
    app.run(debug=True)
