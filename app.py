from flask import Flask

app = Flask(__name__)

@app.route("/")
def Verficações_Lupa():
  return "Verificações Lupa" 
