from leitor import ler_dados    
from menu import exibir_menu    

calcular_ganhos = 0.01

def calcular_ganhos(frequencia):
    return frequencia * calcular_ganhos  

def main():
    dados = ler_dados()  

    while True:  
        escolha, clientes = exibir_menu(dados)  

        if escolha == 0:  
            print("Até!")
            break  

        if escolha < 1 or escolha > len(clientes):
            print("Opção inválida! Tente novamente.\n")
            continue  

        clientes = clientes[escolha - 1]    
        frequencia = dados[clientes]          
        ganhos = calcular_ganhos(frequencia) 

        print(f"\n Cliente:  {clientes}")
        print(f"  Frequência:  {frequencia} treinos por semana")
        print(f" Ganho muscular: {ganhos:.2f}\n")  

main()  
