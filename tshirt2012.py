# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import sys
import datetime
# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'admin'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Returns a new connection to the database."""
    connection = sqlite3.connect(app.config['DATABASE'])
    connection.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
    return connection


def init_db():
    """Creates the database tables."""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    """Make sure we are connected to the database each request."""
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def show_entries():
    cur = g.db.execute('select orderid, sex, typeid, tsize, num, cnname from orders where cnname = ? order by orderid desc', [session['cnname']])
    entries = [dict(orderid=row[0], sex=row[1], typeid=row[2], tsize=row[3], num=row[4], cnname=row[5]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


def output():
    cur = g.db.execute('select orders.orderid, orders.cnname, orders.sex, orders.typeid, orders.tsize, orders.num from orders, users where orders.cnname = users.cnname and users.userclass = ?', ['thucs111'])
    entries = [dict(orderid=row[0], cnname=row[1], sex=row[2], typeid=row[3], tsize=row[4], num=row[5]) for row in cur.fetchall()]
    outfile = file('/home/daodao/thucs111orders.txt', 'w')
    for entry in entries:
        print >> outfile, entry.orderid + ' ' + entry.cnname+ ' ' + entry.sex + ' ' + entry.typeid+ ' ' + entry.tsize + ' ' + entry.num
    outfile.close()





@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into orders (cnname, sex, typeid, tsize, num, createtime) values (?, ?, ?, ?, ?, ?)', [session['cnname'], request.form['sex'], request.form['typeid'], request.form['tsize'], request.form['num'], datetime.datetime.now()])
    g.db.commit()
    flash('New order was successfully posted')
    return redirect(url_for('show_entries'))
    
    
@app.route('/delete', methods=['POST'])
def delete_entry():
    if not session.get('logged_in'):
        abort(401)
        
    order = query_db('select orderid from orders where cnname = ? and orderid = ?', [session['cnname'],request.form['orderid']], True)

    if order is None:
        flash('This is not your order')
        return redirect(url_for('show_entries'))
    else:
        g.db.execute('delete from orders where cnname = ? and orderid = ?', [session['cnname'], request.form['orderid']])
        g.db.commit()
        flash('Order was successfully deleted')
        return redirect(url_for('show_entries'))


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':

        user = query_db('select username, cnname from users where username = ? and password = ? order by userid desc', [request.form['username'], request.form['password']], True)
        if user is None:           
            error = 'Invalid login'
        else:
            
            session['username'] = user['username']
            session['cnname'] = user['cnname']
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
        
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    reload(sys)  
    sys.setdefaultencoding("utf-8")  
    app.run()
