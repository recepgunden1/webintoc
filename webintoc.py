from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps
# kullanici giris decoratoru
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın !!!","danger")
            return redirect(url_for("login"))
    return decorated_function
# Kullanıcı kayıt formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min=4,max=20,message = "En az 4 en çok 20 karakter girmelisiniz")])
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min=4,max=25,message = "En az 4 en çok 25 karakter girmelisiniz")])
    email = StringField("Mail Adresiniz",validators=[validators.Email("Lütfen Geçerli Bir Mail Adresi Giriniz")])
    password = PasswordField("Parola",validators=[validators.Length(min=4),
        validators.DataRequired(message="Lütfen bir parola belirleyin"),
        validators.EqualTo(fieldname = "confirm",message = "Parolalar aynı değil")
    ])
    confirm = PasswordField("Parola Doğrula")

class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")
app = Flask(__name__)

app.secret_key = "webintoc"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "webintoc"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/articles")
@login_required
def articles():
    cursor = mysql.connection.cursor()
    sorgu = "select * from articles"
    result = cursor.execute(sorgu)

    if result > 0:
        articles = cursor.fetchall()
        return render_template("articles.html",articles = articles)
    else:
        return render_template("articles.html")

@app.route("/dashboard")
@login_required
def dashboard():
    cursor = mysql.connection.cursor()
    sorgu = "select * from articles where author = %s"
    result = cursor.execute(sorgu,(session["username"],))

    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashboard.html",articles=articles)

    else:
        return render_template("dashboard.html")

@app.route("/register",methods=["GET","POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()
        sorgu = "insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"

        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()

        flash("Başarıyla kayıt oldunuz !","success")

        return redirect(url_for("login"))
    else:
        return render_template("register.html",form=form)
    
@app.route("/login",methods=["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()
        sorgu = "select * from users where username = %s"

        result = cursor.execute(sorgu, (username,))

        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarıyla giriş yapıldı !","success")
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("index"))
            else:
                flash("Parola veya kullanıcı adı hatalı !!!","danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle bir kullanıcı bulunmuyor !!!","danger")
            return redirect(url_for("login"))
    
    return render_template("login.html",form = form)

@app.route("/article/<string:id>", methods=["GET","POST"])
@login_required
def article(id):
    form = CommentForm(request.form)
    cursor = mysql.connection.cursor()
    sorgu = "select * from articles where id = %s"
    result = cursor.execute(sorgu,(id,))
    
    if result > 0:
        if request.method == "POST" and form.validate():
            comment = form.comment.data
            article_id = id
            sorgu2 = "INSERT INTO comments (article_id, username, comment) VALUES (%s, %s, %s)"
            cursor.execute(sorgu2,(article_id,session["username"], comment))
            mysql.connection.commit()
            cursor.close()
            flash("Yorum başarıyla eklendi", "success")
            return redirect(url_for("index"))
        article = cursor.fetchone()
        return render_template("article.html",article = article,form = form)

    else:
        return(render_template("article.html"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/addarticle", methods=["GET", "POST"])
@login_required
def addarticle():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        print("Title:", title)
        print("Content:", content)

        cursor = mysql.connection.cursor()
        sorgu = "INSERT INTO articles (title, author, content) VALUES (%s, %s, %s)"
        cursor.execute(sorgu, (title, session["username"], content))

        mysql.connection.commit()
        cursor.close()

        flash("Makale başarıyla eklendi", "success")

        return redirect(url_for("dashboard"))

    return render_template("addarticle.html", form=form)


@app.route("/edit/<string:id>",methods=["GET","POST"])
@login_required
def update(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        sorgu = "select * from articles where id = %s and author = %s"
        result = cursor.execute(sorgu,(id,session["username"]))
        
        if result == 0:
            flash("Bu işleme yetkiniz yok","danger")
            return redirect(url_for("index"))
        else:
            article = cursor.fetchone()
            form = ArticleForm()

            form.title.data = article["title"]
            form.content.data = article["content"]
            return render_template("update.html",form=form)
    else:
        form = ArticleForm(request.form)

        newtitle = form.title.data
        newcontent = form.content.data

        sorgu2 = "update articles set title = %s, content = %s where id = %s"

        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(newtitle,newcontent,id))

        mysql.connection.commit()

        flash("Makale başarıyla güncellendi","success")
        return redirect(url_for("dashboard"))

@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    # Kullanıcının makaleyi silme yetkisini kontrol et
    sorgu = "SELECT * FROM articles WHERE author = %s AND id = %s"
    result = cursor.execute(sorgu, (session["username"], id))

    if result > 0:
        # Makaleyi sil
        sorgu2 = "DELETE FROM articles WHERE id = %s"
        cursor.execute(sorgu2, (id,))
        mysql.connection.commit()
        flash("Makale başarıyla silindi", "success")
    else:
        flash("Size ait olmayan bir makaleyi silemezsiniz !!!", "danger")

    cursor.close()
    return redirect(url_for("dashboard"))


class ArticleForm(Form):
    title = StringField("Makale Başlığı",validators=[validators.length(min=4,max=50)])
    content = TextAreaField("Makale içeriği",validators=[validators.length(min=10)])

class CommentForm(Form):
    comment = TextAreaField("",validators=[validators.length(min=1,max=99)])

@app.route("/search",methods=["GET","POST"])
def search():
    if request.method == "GET":
        flash("Bunu yapmaya izniniz yok !","danger")
        return redirect(url_for("index"))
    else:
        keyword = request.form.get("keyword")
        cursor = mysql.connection.cursor()
        sorgu = "select * from articles where title like '%" + keyword + "%' "
        result = cursor.execute(sorgu)

        if result == 0:
            flash("Bu kelimeye uygun makale bulunamadı","warning")
            return redirect(url_for("articles"))
        else:
            articles = cursor.fetchall()
            return render_template("articles.html",articles=articles)
        
if __name__ == "__main__":
    app.run(debug=True)
