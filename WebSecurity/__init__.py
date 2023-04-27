#!/usr/bin/env python3
# using http://blog.luisrei.com/articles/flaskrest.html
# a2 server for CSC8520 - vulnerable to SQL injection and XSS.
# For educational purposes only. Please never resue or misuse it for malicious purpose.
# (Linda)Zhaohui TANG, 2023

from http.cookiejar import Cookie
from flask import Flask, render_template,request,redirect,session,jsonify
import sqlite3
import os
import hashlib
db = "mydb.db"

port = 7007

app = Flask(__name__)
app.secret_key = 'a'

def hash(data):
    """ Wrapper around sha256 """
    return hashlib.sha256(data.replace('\n','').encode('ascii')).hexdigest()

@app.route('/')
def main():
    if not 'username' in session:
        return redirect("/login",303)
    ul = None
    return render_template('main.html', name=session['username'][0], users=ul,news=getNews())

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('form.html')
    elif request.method == 'POST':
        conn = sqlite3.connect('mydb.db')
        c=conn.cursor()
        email = request.form['email']        
        password = hash(request.form['password'])
        print("SELECT * FROM users WHERE email= '%s'' and password='%s'' ",(email,password))
        c.execute("SELECT * FROM users WHERE email= ? and password= ? ",(email,password))
        rval=c.fetchone()
        if email == 'admin@a.com' and password == app.adminhash:
            rval=('admin','admin','admin')
        if rval:
            session['username'] = rval          
            return redirect("/",303)
        else:
            return render_template('form.html', error='Username or password incorrect!')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect("/login",303)    
        

def getNews():
    conn = sqlite3.connect('mydb.db')
    c=conn.cursor()
    return c.execute("SELECT * FROM news").fetchall()

@app.route('/news')
def news():
    if not 'username' in session:
        return redirect("/login",303)
    term = request.args.get('text')
    conn = sqlite3.connect('mydb.db')
    c=conn.cursor()
    print(term)
    c.execute("insert into news (source,text) values (?,?)",(session['username'][0],term))
    conn.commit()
    return render_template('main.html', name=session['username'][0],news=getNews())




if __name__ == '__main__':

    with open('info','r') as f:
        s = f.readlines()
    app.secret_key = s[0].replace('\n','')
    app.adminhash=hash(s[1])
    alicehash=hash(s[2])
    
    try:
        os.remove(db)
    except OSError:
        pass
    conn = sqlite3.connect(db)
    c=conn.cursor()
    c.execute("create table NEWS(source string, text string)")
    c.execute("create table USERS(name string, password string, email string)")
    c.execute("insert into users (email, name,password) values ('alice@alice.com','alice','"+alicehash+"')")
    c.execute("insert into users (email, name,password) values ('admin@admin.com','admin','"+hash("averysecureadminpassword")+"')")
    conn.commit()
    app.config["SESSION_COOKIE_HTTPONLY"]=False
    app.run(debug=False,port=port)
