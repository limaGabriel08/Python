import math
from flask import render_template, request

def calcular():
    # Inicializa as variáveis para garantir que sempre existam
    etapas = ""
    resultado = ""
    
    try:
        num1 = float(request.form.get("num1", 0))
        operacao = request.form.get("operacao")

        if operacao == "sqrt":
            if num1 < 0:
                resultado = "Erro"
                etapas = f"Não existe raiz real de {num1}."
            else:
                resultado = math.sqrt(num1)
                etapas = f"√{num1} = {resultado}"
        else:
            num2_valor = request.form.get("num2", "").strip()
            if not num2_valor:
                return render_template("calculadora.html", etapas="Informe o segundo número.", resultados="")
            
            num2 = float(num2_valor)

            if operacao == "+":
                resultado = num1 + num2
                etapas = f"{num1} + {num2} = {resultado}"
            elif operacao == "-":
                resultado = num1 - num2
                etapas = f"{num1} - {num2} = {resultado}"
            elif operacao == "*":
                resultado = num1 * num2
                etapas = f"{num1} × {num2} = {resultado}"
            elif operacao == "/":
                if num2 == 0:
                    resultado = "Erro"
                    etapas = "Divisão por zero não permitida."
                else:
                    resultado = num1 / num2
                    etapas = f"{num1} ÷ {num2} = {resultado}"
            elif operacao == "**":
                resultado = num1 ** num2
                etapas = f"{num1}^{num2} = {resultado}"

        return render_template("calculadora.html", etapas=etapas, resultados=resultado)

    except Exception as e:
        return render_template("calculadora.html", etapas="Erro nos dados informados", resultados=str(e))
