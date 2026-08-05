import json  

def ler_dados():
    with open("dados_prova_B.json", "r", encoding="utf-8") as f:  
        dados = json.load(f)  
    return dados 
