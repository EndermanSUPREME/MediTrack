# MediTrack
IntroToDatabases Group Project : A Patient &amp; Appointment Management System

# ER - Diagram
found as file ER.png

![ER Diagram](./sql/ER.png)

# SQL Information
All sql data can be found in the folder labeled 'sql'

Our database schema is stored in meditrack(1).sql

A version with example data exists in meditrack(wdata).sql

**BOTH** are in 3nf

# Queries are contained in the DBS_queries.sql file


*They are intended to be run on the wdata database* since the reference real data points

However there structure is not dependent on the data outside of the specific fields like id, time, etc being specific instances

# Compiling the app & connecting database
You must run ```pip install -r requirements.txt``` <br><br>
The Database should be connected automatically

run the flask app with: ``` python ./app.py ```

*Note It will only work while you are on Kent State's Network* - there is a local version in the sql folder (meditrack & data.sql) This can be imported into XAMPP with mysql 

If you go this way, you'll have to change the following section in app.py:

```
# MySQL connection configuration
app.config['MYSQL_HOST'] = '10.37.1.103'
app.config['MYSQL_USER'] = 'yoyojesus'
app.config['MYSQL_PASSWORD'] = 'veryOkIrTIcA'
app.config['MYSQL_DB'] = 'meditrack'
```

TO

```
# MySQL connection configuration for XAMPP
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'meditrack'
```