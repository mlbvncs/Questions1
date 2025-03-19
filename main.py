#IMPORTS FLASK
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user
from flask_mail import Mail, Message
import random

app = Flask(__name__)
#mail
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": '', #Preencher com email
    "MAIL_PASSWORD": '' #Preencher com senha (de preferência gerar senha de aplicativo)
}
app.config.update(mail_settings)
mail = Mail(app)
#login
app.secret_key = "xyxyxyxy"
login_manager = LoginManager(app)
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)
#db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    plan = db.Column(db.String(80), nullable=False)

    def __init__(self, user, email, password, plan):
        self.user = user
        self.email = email
        self.password = password
        self.plan = plan

@app.route("/")
def principal():
    return render_template("principal.html")

@app.route("/entrarnaconta", methods=["GET", "POST"])
def entrarnaconta():
    if request.method == "POST":
        #Pegando todos os dados relacionados ao email (advindo de "/redefinirsenha") digitado (id, user, email e password)
        user = Users.query.filter_by(email=request.form["email"]).first()
        #Mudando a senha e adicionando ao banco de dados
        user.password = request.form["password"]
        db.session.commit()
        return redirect(url_for('entrarnaconta'))
    else:
        #Pegando todos os dados da tabela no banco de dados
        dados = Users.query.all()
        email = []
        senha = []
        #Criando listas separadas com os dados user e email
        for data in dados:
            email1 = data.email
            email.append(email1)

            senha1 = data.password
            senha.append(senha1)
        return render_template("entrarnaconta.html", email=email, senha=senha)
@app.route("/redefinirsenha", methods=["GET", "POST"])
def redefinirsenha():
    if request.method == "POST":
        #Pegando o email
        email = request.form["email"]
        #Gerando um código com 5 números aleatórios
        código = ""
        for contagem in range(5):
            número = random.randint(0, 9)
            código = código + str(número)
        #Enviando o código para um email
        msg = Message(
            subject = 'Contato - Three.ai',
            sender = app.config.get("MAIL_USERNAME"),
            recipients = [email],
            html = render_template("msghtml.html", código=código)
        )
        mail.send(msg)
        return render_template("redefinirsenha2.html", email=email, código=código)
    else:
        #Pegando todos os dados da tabela no banco de dados
        dados = Users.query.all()
        email = []
        #Criando listas separadas com os dados email
        for data in dados:
            email1 = data.email
            email.append(email1)
        return render_template("redefinirsenha1.html", email=email)
@app.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    if request.method == "POST":
        user = Users(user=request.form["user"],
                     email=request.form["email"],
                     password=request.form["password"],
                     plan='sem plano')
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('entrarnaconta'))
    else:
        #Pegando todos os dados da tabela no banco de dados
        dados = Users.query.all()
        user = []
        email = []
        #Criando listas separadas com os dados user e email
        for data in dados:
            user1 = data.user
            user.append(user1)

            email1 = data.email
            email.append(email1)
        return render_template("criarconta.html", user=user, email=email)
@app.route("/usuário", methods=["GET", "POST"])
def usuário():
    if request.method == "POST":
        #Pegando todos os dados relacionados ao email (advindo de "/criarconta") digitado (id, user, email e password)
        user = Users.query.filter_by(email=request.form["email"]).first()
        #Efetuando login do usuário
        login_user(user)
        return render_template("usuário.html")
    else:
        return render_template("usuário.html")
#observar "/logout"
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("entrarnaconta"))
@app.route("/excluirconta", methods=["GET", "POST"])
def excluirconta():
    if request.method == "POST":
        #Pegando o email
        email = request.form["email"]
        #Gerando um código com 5 números aleatórios
        código = ""
        for contagem in range(5):
            número = random.randint(0, 9)
            código = código + str(número)
        #Enviando o código para um email
        msg = Message(
            subject='Contato - Three.ai',
            sender=app.config.get("MAIL_USERNAME"),
            recipients=[email],
            html=render_template("msghtml.html", código=código)
        )
        mail.send(msg)
        return render_template("excluirconta2.html", email=email, código=código)
    else:
        #Pegando todos os dados da tabela no banco de dados
        dados = Users.query.all()
        email = []
        #Criando listas separadas com os dados email
        for data in dados:
            email1 = data.email
            email.append(email1)
        return render_template("excluirconta1.html", email=email)
@app.route("/excluircontaadicional", methods=["POST"])
def excluircontaadicional():
    if request.method == "POST":
        #Pegando todos os dados relacionados ao email (advindo de "/excluirconta") digitado (id, user, email e password)
        user = Users.query.filter_by(email=request.form["email"]).first()
        #Excluindo a conta (já faz logout automaticamente)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('criarconta'))

@app.route("/questões")
def questões():
    return render_template("questões.html")
@app.route("/escolherquestão")
def escolherquestão():
    return render_template("escolherquestão1.html")


if __name__ == "__main__":
    #Para o db.create_all() funcionar
    app.app_context().push()
    #Criando o banco de dados
    db.create_all()
    app.run(debug=True)