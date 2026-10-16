# Importación
from flask import Flask, render_template, request, redirect, session
# Conexión de la biblioteca de bases de datos
from flask_sqlalchemy import SQLAlchemy
# Importar la librería de síntesis de voz
import pyttsx3

app = Flask(__name__)
# Establecer la clave secreta para la sesión.
app.secret_key = 'my_top_secret_123'
# Estableciendo conexión SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Creando la DB
db = SQLAlchemy(app)

# Inicializar motor de voz de pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Velocidad de lectura
engine.setProperty('volume', 0.9)  # Volumen


def hablar(texto):
  "Función auxiliar para reproducir texto en voz alta desde el servidor"
  print(f'🤖 Voz del Servidor > {texto}')
  engine.say(texto)
  engine.runAndWait()


# Creando la tabla de tarjetas
class Card(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  subtitle = db.Column(db.String(300), nullable=False)
  text = db.Column(db.Text, nullable=False)
  user_email = db.Column(db.String(100), nullable=False)

  def __repr__(self):
    return f'<Card {self.id}>'


# Tarea #1. Crear la tabla de usuarios
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  email = db.Column(db.String(100), nullable=False)
  password = db.Column(db.String(30), nullable=False)


# Lanzamiento de la página de contenido (Login)
@app.route('/', methods=['GET', 'POST'])
def login():
  error = ''
  if request.method == 'POST':
    form_login = request.form['email']
    form_password = request.form['password']

    users_db = User.query.all()
    for user in users_db:
      if form_login == user.email and form_password == user.password:
        session['user_email'] = user.email
        # ¡Integración de voz! Anuncia el inicio de sesión exitoso
        hablar(f'Bienvenido de nuevo, usuario con correo {user.email}')
        return redirect('/index')

    error = 'Nombre de usuario o contraseña incorrectos'
    hablar('Intento de inicio de sesión fallido.')
    return render_template('login.html', error=error)
  else:
    return render_template('login.html')


@app.route('/reg', methods=['GET', 'POST'])
def reg():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']

    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()

    # ¡Integración de voz! Anuncia el registro
    hablar('Nuevo usuario registrado con éxito en el diario.')
    return redirect('/')
  else:
    return render_template('registration.html')


# Iniciar página de contenido
@app.route('/index')
def index():
  email = session.get('user_email')
  cards = Card.query.filter_by(user_email=email).all()
  return render_template('index.html', cards=cards)


@app.route('/logout')
def logout():
  email = session.get('user_email', 'usuario')
  session.pop('user_email', None)
  hablar('Sesión cerrada correctamente.')
  return redirect('/')


# Lanzando la página de la tarjeta
@app.route('/card/<int:id>')
def card(id):
  card = Card.query.get(id)
  # ¡Integración de voz extra! Lee el título de la tarjeta en voz alta al abrirla
  if card:
    hablar(f'Abriendo tarjeta titulada: {card.title}')
  return render_template('card.html', card=card)


# Iniciando la página de creación de tarjetas
@app.route('/create')
def create():
  return render_template('create_card.html')


@app.route('/form_create', methods=['GET', 'POST'])
def form_create():
  if request.method == 'POST':
    title = request.form['title']
    subtitle = request.form['subtitle']
    text = request.form['text']
    email = session['user_email']

    card = Card(title=title, subtitle=subtitle, text=text, user_email=email)
    db.session.add(card)
    db.session.commit()

    # ¡Integración de voz! Anuncia la creación de la nota
    hablar(f'Nueva tarjeta de diario creada: {title}')
    return redirect('/index')
  else:
    return render_template('create_card.html')


if __name__ == '__main__':
  hablar('Iniciando servidor web del diario personal.')
  app.run(debug=True)
