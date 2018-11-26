#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "xl2685"
DB_PASSWORD = "43q85ei8"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)

email = ''
# Here we create a test table and insert some values in it
############### check if test table extist in cloud db
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/verify', methods=['POST'])
def verify():
   email = request.form['uname']
   password = request.form['psw']
   if request.form["action"] == 'log in':
      cmd_check = 'SELECT count(*) from user_indi where email = (:name1)';
      result_check = g.conn.execute(text(cmd_check), name1 = email);
      if result_check.fetchone()[0] == 1:
          cmd = 'SELECT password FROM user_indi WHERE email = (:name1)';
          result = g.conn.execute(text(cmd), name1 = email);
          if password == result.fetchone()[0]:
              return render_template("search_info.html")
          else:
              return "please enter valid email and password."
      else:
           return "You haven't signed up, <br><a href = '/'></b>" + \
              "please sign up first</b></a>"
   else:
      cmd = 'INSERT INTO user_indi VALUES (:name1, :name2, :name3)';
      g.conn.execute(text(cmd), name1 = email, name2 = password, name3 = 'f');
      return "You have registered successfully, <br><a href = '/'></b>" + \
         "please log in</b></a>"
      # return redirect('search_info')


@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   email = ''
   return render_template("index.html")

@app.route('/add', methods=['POST'])
def add():
  email = request.form['email']
  comment = request.form['comment']
  valueformoney = request.form['valueformoney']
  foodbeverages = request.form['foodbeverages']
  entertainment = request.form['entertainment']
  delay = request.form['delay']
  seatcomfortable = request.form['seatcomfortable']
  staffservice = request.form['staffservice']
  cmd = 'INSERT INTO travelrecord VALUES (:name1, :name2, :name3, :name4, :name5, :name6, :name7, :name8, :name9, :name10)';
# ####################flightid
  g.conn.execute(text(cmd), name1 = email, name2 =  2018102307, name3 = comment, name4 = valueformoney, name5 = foodbeverages, name6 = entertainment, name7 = delay, name8 = seatcomfortable, name9 = staffservice, name10 = 'f');
  return "You have added your record successfully, <br><a href = '/record_trip'></b>" + \
     "you can go back here</b></a>"


# cursor = g.conn.execute("SELECT name FROM test")
#   names = []
#   for result in cursor:
#     names.append(result['name'])  # can also be accessed using result[0]
#   cursor.close()

  context = dict(data = names)
@app.route('/search_info_result', methods=['POST'])
def search_info_result():
    departure = request.form['departure']
    arrival = request.form['arrival']
    # rating = request.form['rating']
    cmd = 'SELECT AirCompany, \
                  (AVG(ValueForMoney)+AVG(FoodBeverages)+ AVG(Entertainment)+ AVG(Delay)+ AVG(SeatComfortable)+ AVG(StaffService))/6 as Overall, \
                  AVG(ValueForMoney) as ValueForMoney, \
                  AVG(FoodBeverages) as FoodBeverages, \
                  AVG(Entertainment) as Entertainment, \
                  AVG(Delay) as Delay, \
                  AVG(SeatComfortable) as SeatComfortable, \
                  AVG(StaffService) as StaffService \
            FROM TravelRecord as t ,flight as f, airline as a \
            WHERE f.flightid = t.flightid AND a.AirlineCode = f.AirlineCode AND departureairport= :name1 AND arrivalairport = :name2 \
            GROUP BY f.AirlineCode, AirCompany \
            ORDER BY Overall DESC';
            # ORDER BY Overall Desc
    cursor = g.conn.execute(text(cmd), name1 = departure, name2 = arrival);
    names = []
    airline = []
    for result in cursor:
        info_one = [result[0],
                    round(result[1], 2),
                    round(result[2], 2),
                    round(result[3], 2),
                    round(result[4], 2),
                    round(result[5], 2),
                    round(result[6], 2),
                    round(result[7], 2)]
        names.append(info_one)  # can also be accessed using result[0]
        airline.append(result[0])
    # print names
    context = dict(data = names)
    # print context
    cursor.close()
    return render_template("search_info.html", **context)
  # return render_template("search_info.html")

@app.route('/search_info')
def search_info():
  return render_template("search_info.html")

@app.route('/detail_info')
def detail():
  return render_template("detail_info.html")

@app.route('/record_trip')
def record():
   return render_template("record_trip.html")



# @app.route('/login')
# def login():
#     abort(401)
#     this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
