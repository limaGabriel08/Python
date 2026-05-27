from flask import Flask, render_template, request
from calculadora import calcular

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST']) # Adicione os métodos aqui
def index():
    if request.method == 'POST':
        return calcular() # Chama a lógica do outro arquivo
    return render_template('calculadora.html', etapas='', resultados='')

@app.route('/calcular', methods=['POST'])
def calcular_route():
    return calcular()



if __name__ == '__main__':
    app.run(debug=True) 
