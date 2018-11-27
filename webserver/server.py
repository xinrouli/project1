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
              return  "please enter valid email and password, <br><a href = '/'></b>" + \
                 "you can go back here</b></a>"
      else:
           return "You haven't signed up, <br><a href = '/'></b>" + \
              "please sign up first</b></a>"
   else:
      cmd = 'INSERT INTO user_indi VALUES (:name1, :name2, :name3)';
      g.conn.execute(text(cmd), name1 = email, name2 = password, name3 = 'f');
      return "You have registered successfully, <br><a href = '/'></b>" + \
         "please log in</b></a>"


@app.route('/logout')
def logout():
   email = ''
   return render_template("index.html")

@app.route('/add', methods=['POST'])
def add():
  email = request.form['email']

  airlinecode = request.form['airlinecode']
  flightnumber = request.form['flightnumber']
  aircraftcode = request.form['aircraftcode']
  date = request.form['date']
  arrivalairport = request.form['arrivalairport']
  arrivalterminal = request.form['arrivalterminal']
  departureairport = request.form['departureairport']
  departureterminal = request.form['departureterminal']

  comment = request.form['comment']
  valueformoney = request.form['valueformoney']
  foodbeverages = request.form['foodbeverages']
  entertainment = request.form['entertainment']
  delay = request.form['delay']
  seatcomfortable = request.form['seatcomfortable']
  staffservice = request.form['staffservice']

  cmd_arr = 'SELECT count(*) from terminal where airportcode = :name1 and terminalname = :name2';
  result_arr = g.conn.execute(text(cmd_arr), name1 = arrivalairport, name2 = arrivalterminal);
  if result_arr.fetchone()[0] != 1:
      return "Please enter a valid arrival airport and arrival terminal, <br><a href = '/record_trip'></b>" + \
             "You can re-fill the form here</b></a>"
  else:
     cmd_dep = 'SELECT count(*) from terminal where airportcode = :name1 and terminalname = :name2';
     result_dep = g.conn.execute(text(cmd_dep), name1 = departureairport, name2 = departureterminal);
     if result_dep.fetchone()[0] != 1:
         return "Please enter a valid departure airport and departure terminal, <br><a href = '/record_trip'></b>" + \
                "You can re-fill the form here</b></a>"
     else:
         cmd_airline = 'SELECT count(*) from airline where airlinecode = :name1 ';
         result_airline = g.conn.execute(text(cmd_airline), name1 = airlinecode);
         if result_airline.fetchone()[0] != 1:
             return "Please enter a valid airline code, <br><a href = '/record_trip'></b>" + \
                    "You can re-fill the form here</b></a>"
         else:
            cmd_aircraft = 'SELECT count(*) from aircraft where aircraftcode = :name1 ';
            result_aircraft = g.conn.execute(text(cmd_aircraft), name1 = aircraftcode);
            if result_aircraft.fetchone()[0] != 1:
                return "Please enter a valid aircraft code, <br><a href = '/record_trip'></b>" + \
                       "You can re-fill the form here</b></a>"
            else:
               cmd_email = 'SELECT count(*) from user_indi where email = :name1 ';
               result_email = g.conn.execute(text(cmd_email), name1 = email);
               if result_email.fetchone()[0] != 1:
                   return "Please enter a valid user email, <br><a href = '/record_trip'></b>" + \
                          "You can re-fill the form here</b></a>"
               else:
                     cmd_id = 'SELECT count(*) from flight \
                                where airlinecode = :name1 \
                                    and flightnumber = :name2 \
                                    and date = :name3 \
                                    and arrivalairport = :name4 \
                                    and arrivalterminal  = :name5 \
                                    and departureairport = :name6 \
                                    and departureterminal = :name7';
                     result_id = g.conn.execute(text(cmd_id), name1 = airlinecode, name2= flightnumber, name3=date, name4=arrivalairport, name5=arrivalterminal, name6=departureairport, name7=departureterminal);
                     if result_id.fetchone()[0] != 1:
                         cmd_insert = 'INSERT into flight \
                                    VALUES((select count(*) from flight)+1, \
                                    :name1, :name2, :name3, :name4, :name5, :name6, :name7, :name8, :name9)';
                         result_insert = g.conn.execute(text(cmd_insert), name1 = aircraftcode, name2 = airlinecode, name3= flightnumber, name4=arrivalairport, name5=arrivalterminal, name6=departureairport, name7=departureterminal, name8=date, name9='f');
                         cmd_flightid = 'SELECT flightid from flight \
                                        where airlinecode = :name1 \
                                            and flightnumber = :name2 \
                                            and date = :name3 \
                                            and arrivalairport = :name4 \
                                            and arrivalterminal  = :name5 \
                                            and departureairport = :name6 \
                                            and departureterminal = :name7';
                         result_flightid = g.conn.execute(text(cmd_flightid), name1 = airlinecode, name2= flightnumber, name3=date, name4=arrivalairport, name5=arrivalterminal, name6=departureairport, name7=departureterminal);
                         flightid = result_flightid.fetchone()[0]

                         cmd = 'INSERT INTO travelrecord VALUES (:name1, :name2, :name3, :name4, :name5, :name6, :name7, :name8, :name9, :name10)';
                         g.conn.execute(text(cmd), name1 = email, name2 =  flightid, name3 = comment, name4 = valueformoney, name5 = foodbeverages, name6 = entertainment, name7 = delay, name8 = seatcomfortable, name9 = staffservice, name10 = 'f')
                     else:
                         cmd_flightid = 'SELECT flightid from flight \
                                        where airlinecode = :name1 \
                                            and flightnumber = :name2 \
                                            and date = :name3 \
                                            and arrivalairport = :name4 \
                                            and arrivalterminal  = :name5 \
                                            and departureairport = :name6 \
                                            and departureterminal = :name7';
                         result_flightid = g.conn.execute(text(cmd_flightid), name1 = airlinecode, name2= flightnumber, name3=date, name4=arrivalairport, name5=arrivalterminal, name6=departureairport, name7=departureterminal);
                         flightid = result_flightid.fetchone()[0]

                         cmd = 'INSERT INTO travelrecord VALUES (:name1, :name2, :name3, :name4, :name5, :name6, :name7, :name8, :name9, :name10)';
                         g.conn.execute(text(cmd), name1 = email, name2 =  flightid, name3 = comment, name4 = valueformoney, name5 = foodbeverages, name6 = entertainment, name7 = delay, name8 = seatcomfortable, name9 = staffservice, name10 = 'f')
  return "You have added your record successfully, <br><a href = '/record_trip'></b>" + \
     "please go back here</b></a>"



@app.route('/search_info_result', methods=['POST'])
def search_info_result():
    departure = request.form['departure']
    arrival = request.form['arrival']
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
    cursor = g.conn.execute(text(cmd), name1 = departure, name2 = arrival);
    names = []
    for result in cursor:
        info_one = [result[0],
                    round(result[1], 2),
                    round(result[2], 2),
                    round(result[3], 2),
                    round(result[4], 2),
                    round(result[5], 2),
                    round(result[6], 2),
                    round(result[7], 2)]
        names.append(info_one)
    if names == []:
        return "There is no record matching your criteria, <br><a href = '/search_info'></b>" + \
             "you can redefine your search here.</b></a>"
    else:
        context = dict(data = names)
        cursor.close()
        return render_template("search_info.html", **context)

@app.route('/search_detail', methods=['POST'])
def search_detail():
    departure = request.form['departure']
    arrival = request.form['arrival']
    airline = request.form['airline']
    cmd = 'SELECT FlightNumber, \
                ValueForMoney, FoodBeverages, Entertainment, Delay, SeatComfortable, StaffService, Comments, \
                DepartureAirport, DepartureTerminal, apd.city, apd.state, \
                ArrivalAirport, ArrivalTerminal, apa.city, apa.state, \
                date, AirAlliance, Capacity \
            FROM TravelRecord as t ,flight as f, airline as a, aircraft as af, airport as apa, airport as apd \
            WHERE f.flightid = t.flightid AND a.AirlineCode = f.AirlineCode AND af.AircraftCode=f.AircraftCode \
            AND apd.AirportCode = f.departureairport AND apa.AirportCode = f.ArrivalAirport \
            AND departureairport = :name1 AND arrivalairport = :name2 AND AirCompany = :name3 \
            ORDER BY FlightNumber DESC';
    cursor = g.conn.execute(text(cmd), name1 = departure, name2 = arrival, name3 = airline);
    names = []
    for result in cursor:
        info_one = [result[0],
                    round(result[1], 2),
                    round(result[2], 2),
                    round(result[3], 2),
                    round(result[4], 2),
                    round(result[5], 2),
                    round(result[6], 2),
                    result[7],
                    result[8],
                    result[9],
                    result[10],
                    result[11],
                    result[12],
                    result[13],
                    result[14],
                    result[15],
                    result[16],
                    result[17],
                    result[18],
                    airline]
        names.append(info_one)
    if names == []:
        return "There is no record matching your criteria, <br><a href = '/search_info'></b>" + \
             "you can redefine your search here.</b></a>"
    else:
        context = dict(data = names)
        cursor.close()
        return render_template("detail_info.html", **context)

@app.route('/search_user_detail', methods=['POST'])
def search_user_detail():
    email = request.form['email']
    password = request.form['password']
    cmd_check = 'SELECT count(*) from user_indi where email = (:name1)';
    result_check = g.conn.execute(text(cmd_check), name1 = email);
    if result_check.fetchone()[0] == 1:
        cmd_pass = 'SELECT password FROM user_indi WHERE email = (:name1)';
        result_pass = g.conn.execute(text(cmd_pass), name1 = email);
        if password == result_pass.fetchone()[0]:
            cmd = 'SELECT AirCompany,FlightNumber, \
                            ValueForMoney, FoodBeverages, Entertainment, Delay, SeatComfortable, StaffService, Comments, \
                            DepartureAirport, DepartureTerminal, apd.city, apd.state, \
                            ArrivalAirport, ArrivalTerminal, apa.city, apa.state, \
                            date, AirAlliance, Capacity \
                        FROM TravelRecord as t ,flight as f, airline as a, aircraft as af, airport as apa, airport as apd, user_indi as u \
                        WHERE t.email=u.email AND u.password = :name1 AND u.email = :name2 \
                        AND f.flightid = t.flightid AND a.AirlineCode = f.AirlineCode AND af.AircraftCode=f.AircraftCode \
                        AND apd.AirportCode = f.departureairport AND apa.AirportCode = f.ArrivalAirport \
                        ORDER BY FlightNumber DESC';
            cursor = g.conn.execute(text(cmd), name1 = password, name2 = email);
            names = []
            for result in cursor:
                info_one = [result[0],
                            result[1],
                            round(result[2], 2),
                            round(result[3], 2),
                            round(result[4], 2),
                            round(result[5], 2),
                            round(result[6], 2),
                            round(result[7], 2),
                            result[8],
                            result[9],
                            result[10],
                            result[11],
                            result[12],
                            result[13],
                            result[14],
                            result[15],
                            result[16],
                            result[17],
                            result[18],
                            result[19]]
                names.append(info_one)
            if names == []:
                return "You have add any flight record yet, <br><a href = '/record_trip'></b>" + \
                     "you can add your record here.</b></a>"
            else:
                context = dict(data = names)
                cursor.close()
                return render_template("user_detail.html", **context)
        else:
            return  "please enter valid email and password, <br><a href = '/user_detail'></b>" + \
               "you can go back here</b></a>"
    else:
        return "You haven't signed up this email yet, <br><a href = '/'></b>" + \
              "you can sign up this email here</b></a>"


@app.route('/search_info')
def search_info():
  return render_template("search_info.html")

@app.route('/detail_info')
def detail():
  return render_template("detail_info.html")

@app.route('/record_trip')
def record():
   return render_template("record_trip.html")

@app.route('/user_detail')
def user_detail():
  return render_template("user_detail.html")

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
