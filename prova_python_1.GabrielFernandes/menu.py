
def exibir_menu(dados):
    print("=== ACADEMIA FORÇA MAROMBEIRO ===")  

    clientes = list(dados.keys())  

    
    for i, clientes in enumerate(clientes):
        print(f"{i + 1} - {clientes}")  

    print("0 - Sair")  

    escolha = int(input("Escolha o cliente para ver seus ganhos! "))  

    return escolha, clientes  
