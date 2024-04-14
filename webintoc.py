from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
import sqlite3 as sql

app = Flask(__name__)
con = sql.connect("webintoc.db")
cursor = con.cursor()

# Kullanıcı kayıt formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min = 4, max = 25)])
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min = 4, max = 15)])
    email = StringField("Email adresi",validators=[validators.Email(message="Lütfen geçerli bir email adresi giriniz.")])
    password = PasswordField("Parola",validators=[
        validators.DataRequired(message="Lütfen bir parola belirleyiniz."),
        validators.EqualTo(fieldname="confirm",message="Parolanız uyuşmuyor")
    ])
    confirm = PasswordField("Parola Tekrar")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register",methods=["GET","POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST":
        return redirect(url_for("index"))
    else:
        return render_template("register.html",form = form)

if __name__ == "__main__":
    app.run(debug=True)