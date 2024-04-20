from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = "webintoc"

#######################
#Kullanıcı kayıt formu
#######################
class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min = 4, max = 25)])
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min = 4, max = 15)])
    email = StringField("Email adresi",validators=[validators.Email(message="Lütfen geçerli bir email adresi giriniz.")])
    password = PasswordField("Parola",validators=[
        validators.DataRequired(message="Lütfen bir parola belirleyiniz."),
        validators.EqualTo(fieldname="confirm",message="Parolanız uyuşmuyor")
    ])
    confirm = PasswordField("Parola Tekrar")

#######################
#Kullanıcı giriş formu
#######################
class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")

#######################
#Ana Sayfa
#######################
@app.route("/")
def index():
    return render_template("index.html")

#######################
#Hakkımızda
#######################
@app.route("/about")
def about():
    return render_template("about.html")

#######################
#Kayıt Ol
#######################
@app.route("/register",methods=["GET","POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data 
        password = sha256_crypt.encrypt(form.password.data)

        with sql.connect("webintoc.db") as con:
            cursor = con.cursor()
            sorgu = "INSERT INTO users(name, email, username, password) VALUES (?, ?, ?, ?)"
            cursor.execute(sorgu, (name, email, username, password))
            con.commit()
            
        flash("Başarıyla kayıt oldunuz!","success")
        return redirect(url_for("login"))
    else:
        return render_template("register.html",form = form)

#######################
#Giriş Yap
#######################
@app.route("/login", methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)
    return render_template("login.html",form = form)

if __name__ == "__main__":
    app.run(debug=True)