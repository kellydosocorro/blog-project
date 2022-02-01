from json.tool import main
from flask import Flask, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
  return "Index"

@app.route("/hello/") # Se colocar com barra no final, ele aceita mesmo que no navegador coloque sem a barra
@app.route("/hello/<nome>") #Se não colocar nada além do parâmetro, ele será uma string
def teste(nome = ""):
  return "<h1>Hello, {}</h1>".format(nome)

@app.route("/teste/<int:num>") # Também é possível definir se o parâmetro é um número inteiro ou mesmo float
def teste2(num):
  return "<p>Este é o número {}</p>".format(num)

@app.route("/admin/<user>")
def admin(user):
  return "<h1>Hello {}!</h1>".format(user)

@app.route("/guest/<user>")
def guest(user):
  return "<h1>Hello guest, {}</h1>".format(user)

@app.route("/user/<name>")
def user(name):
  if name == 'admin':
    return redirect(url_for('admin', user=name))
  else:
    return redirect(url_for('guest', user=name))

@app.route("/google/")
def google():
  return redirect('http://www.google.com.br')

if __name__ == '__main__':
  app.run()