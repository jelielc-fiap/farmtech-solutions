import json
from datetime import datetime

cadastros = []

def ler_texto(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor == "":
            print("Entrada inválida. Digite um texto.")
        else:
            return valor

def ler_opcao_inteira(mensagem, minimo=None, maximo=None):
    while True:
        try:
            valor = int(input(mensagem))
            if minimo is not None and valor < minimo:
                print(f"Digite um número maior ou igual a {minimo}.")
            elif maximo is not None and valor > maximo:
                print(f"Digite um número menor ou igual a {maximo}.")
            else:
                return valor
        except ValueError:
            print("Valor inválido. Digite um número inteiro.")

def ler_numero_float(mensagem, minimo=None):
    while True:
        try:
            valor = float(input(mensagem).replace(",", "."))
            if minimo is not None and valor < minimo:
                print(f"Digite um número maior ou igual a {minimo}.")
            else:
                return valor
        except ValueError:
            print("Valor inválido. Digite um número numérico.")

def escolher_cultura():
    while True:
        print("\n=== Escolha a cultura ===")
        print("1 - Café (Área retangular)")
        print("2 - Milho (Área triangular)")

        opcao = ler_opcao_inteira("Opção: ", 1, 2)

        if opcao == 1:
            return "Café"
        elif opcao == 2:
            return "Milho"

def calcular_area(cultura):
    print(f"\n=== Cálculo da área para {cultura} ===")

    if cultura == "Café":
        print("Figura geométrica escolhida: Retângulo")
        largura = ler_numero_float("Informe a largura do terreno em metros: ", 0.01)
        comprimento = ler_numero_float("Informe o comprimento do terreno em metros: ", 0.01)
        area = largura * comprimento

        dados_area = {
            "figura": "Retângulo",
            "largura_m": largura,
            "comprimento_m": comprimento,
            "area_m2": area
        }

    elif cultura == "Milho":
        print("Figura geométrica escolhida: Triângulo")
        base = ler_numero_float("Informe a base do terreno em metros: ", 0.01)
        altura = ler_numero_float("Informe a altura do terreno em metros: ", 0.01)
        area = (base * altura) / 2

        dados_area = {
            "figura": "Triângulo",
            "base_m": base,
            "altura_m": altura,
            "area_m2": area
        }

    return dados_area

def calcular_insumo(cultura):
    print(f"\n=== Cadastro de insumo para {cultura} ===")

    produto = ler_texto("Informe o nome do produto/insumo: ")
    quantidade_ml_por_metro = ler_numero_float("Informe a quantidade em mL por metro: ", 0.01)
    quantidade_ruas = ler_opcao_inteira("Informe a quantidade de ruas da lavoura: ", 1)
    comprimento_cada_rua = ler_numero_float("Informe o comprimento de cada rua em metros: ", 0.01)

    total_metros = quantidade_ruas * comprimento_cada_rua
    total_ml = total_metros * quantidade_ml_por_metro
    total_litros = total_ml / 1000

    dados_insumo = {
        "produto": produto,
        "quantidade_ml_por_metro": quantidade_ml_por_metro,
        "quantidade_ruas": quantidade_ruas,
        "comprimento_cada_rua_m": comprimento_cada_rua,
        "total_metros_aplicacao": total_metros,
        "total_necessario_ml": total_ml,
        "total_necessario_litros": total_litros
    }

    return dados_insumo

def cadastrar_dados():
    print("\n==============================")
    print("      ENTRADA DE DADOS")
    print("==============================")

    nome_responsavel = ler_texto("Informe o nome do responsável: ")
    nome_fazenda = ler_texto("Informe o nome da fazenda: ")
    cultura = escolher_cultura()

    dados_area = calcular_area(cultura)
    primeiro_insumo = calcular_insumo(cultura)

    cadastro = {
        "responsavel": nome_responsavel,
        "fazenda": nome_fazenda,
        "cultura": cultura,
        "area_plantio": dados_area,
        "manejo_insumos": [primeiro_insumo]
    }

    cadastros.append(cadastro)
    print("\nCadastro realizado com sucesso!")

def exibir_dados():
    print("\n==============================")
    print("       SAÍDA DE DADOS")
    print("==============================")

    if len(cadastros) == 0:
        print("Nenhum cadastro encontrado.")
        return

    for i in range(len(cadastros)):
        cadastro = cadastros[i]
        print(f"\n--- Cadastro [{i}] ---")
        print(f"Responsável: {cadastro['responsavel']}")
        print(f"Fazenda: {cadastro['fazenda']}")
        print(f"Cultura: {cadastro['cultura']}")

        area = cadastro["area_plantio"]
        print("Área de Plantio:")
        for chave, valor in area.items():
            print(f"  {chave}: {valor}")

        print("Manejo de Insumos:")
        if len(cadastro["manejo_insumos"]) == 0:
            print("  Nenhum insumo cadastrado.")
        else:
            for j in range(len(cadastro["manejo_insumos"])):
                insumo = cadastro["manejo_insumos"][j]
                print(f"  Insumo [{j}]")
                for chave, valor in insumo.items():
                    print(f"    {chave}: {valor}")

    print("\nJSON gerado com os dados cadastrados:")
    print(json.dumps(cadastros, indent=4, ensure_ascii=False))

def exibir_indices():
    print("\nCadastros disponíveis:")
    for i in range(len(cadastros)):
        print(f"[{i}] {cadastros[i]['fazenda']} - {cadastros[i]['cultura']}")

def atualizar_dados():
    print("\n==============================")
    print("     ATUALIZAÇÃO DE DADOS")
    print("==============================")

    if len(cadastros) == 0:
        print("Nenhum cadastro disponível para atualização.")
        return

    exibir_indices()
    indice = ler_opcao_inteira("Informe o índice do cadastro que deseja atualizar: ", 0, len(cadastros) - 1)
    cadastro = cadastros[indice]

    while True:
        print(f"\nCadastro selecionado: {cadastro['fazenda']} - {cadastro['cultura']}")
        print("1 - Atualizar responsável")
        print("2 - Atualizar nome da fazenda")
        print("3 - Atualizar cultura")
        print("4 - Atualizar área de plantio")
        print("5 - Atualizar um insumo existente")
        print("6 - Voltar ao menu principal")

        opcao = ler_opcao_inteira("Escolha o dado que deseja atualizar: ", 1, 6)

        if opcao == 1:
            cadastro["responsavel"] = ler_texto("Informe o novo nome do responsável: ")
            print("Responsável atualizado com sucesso!")

        elif opcao == 2:
            cadastro["fazenda"] = ler_texto("Informe o novo nome da fazenda: ")
            print("Nome da fazenda atualizado com sucesso!")

        elif opcao == 3:
            nova_cultura = escolher_cultura()
            cadastro["cultura"] = nova_cultura
            cadastro["area_plantio"] = calcular_area(nova_cultura)
            print("Cultura e área de plantio atualizadas com sucesso!")

        elif opcao == 4:
            cadastro["area_plantio"] = calcular_area(cadastro["cultura"])
            print("Área de plantio atualizada com sucesso!")

        elif opcao == 5:
            if len(cadastro["manejo_insumos"]) == 0:
                print("Esse cadastro não possui insumos para atualizar.")
            else:
                print("\nInsumos cadastrados:")
                for i in range(len(cadastro["manejo_insumos"])):
                    insumo = cadastro["manejo_insumos"][i]
                    print(f"[{i}] {insumo['produto']}")

                indice_insumo = ler_opcao_inteira(
                    "Informe o índice do insumo que deseja atualizar: ",
                    0,
                    len(cadastro["manejo_insumos"]) - 1
                )

                while True:
                    insumo = cadastro["manejo_insumos"][indice_insumo]

                    print(f"\nInsumo selecionado: {insumo['produto']}")
                    print("1 - Atualizar produto")
                    print("2 - Atualizar quantidade em mL por metro")
                    print("3 - Atualizar quantidade de ruas")
                    print("4 - Atualizar comprimento de cada rua")
                    print("5 - Recalcular e atualizar todos os dados do insumo")
                    print("6 - Voltar")

                    opcao_insumo = ler_opcao_inteira("Escolha o dado do insumo que deseja atualizar: ", 1, 6)

                    if opcao_insumo == 1:
                        insumo["produto"] = ler_texto("Informe o novo nome do produto/insumo: ")
                        print("Produto atualizado com sucesso!")

                    elif opcao_insumo == 2:
                        insumo["quantidade_ml_por_metro"] = ler_numero_float(
                            "Informe a nova quantidade em mL por metro: ", 0.01
                        )
                        insumo["total_necessario_ml"] = (
                            insumo["quantidade_ruas"]
                            * insumo["comprimento_cada_rua_m"]
                            * insumo["quantidade_ml_por_metro"]
                        )
                        insumo["total_necessario_litros"] = insumo["total_necessario_ml"] / 1000
                        print("Quantidade em mL por metro atualizada com sucesso!")

                    elif opcao_insumo == 3:
                        insumo["quantidade_ruas"] = ler_opcao_inteira(
                            "Informe a nova quantidade de ruas: ", 1
                        )
                        insumo["total_metros_aplicacao"] = (
                            insumo["quantidade_ruas"] * insumo["comprimento_cada_rua_m"]
                        )
                        insumo["total_necessario_ml"] = (
                            insumo["total_metros_aplicacao"] * insumo["quantidade_ml_por_metro"]
                        )
                        insumo["total_necessario_litros"] = insumo["total_necessario_ml"] / 1000
                        print("Quantidade de ruas atualizada com sucesso!")

                    elif opcao_insumo == 4:
                        insumo["comprimento_cada_rua_m"] = ler_numero_float(
                            "Informe o novo comprimento de cada rua em metros: ", 0.01
                        )
                        insumo["total_metros_aplicacao"] = (
                            insumo["quantidade_ruas"] * insumo["comprimento_cada_rua_m"]
                        )
                        insumo["total_necessario_ml"] = (
                            insumo["total_metros_aplicacao"] * insumo["quantidade_ml_por_metro"]
                        )
                        insumo["total_necessario_litros"] = insumo["total_necessario_ml"] / 1000
                        print("Comprimento de cada rua atualizado com sucesso!")

                    elif opcao_insumo == 5:
                        cadastro["manejo_insumos"][indice_insumo] = calcular_insumo(cadastro["cultura"])
                        print("Insumo atualizado com sucesso!")

                    elif opcao_insumo == 6:
                        break

        elif opcao == 6:
            break

def adicionar_insumo_em_cadastro():
    print("\n==============================")
    print("   ADICIONAR INSUMO EM CADASTRO")
    print("==============================")

    if len(cadastros) == 0:
        print("Nenhum cadastro disponível para adicionar insumos.")
        return

    exibir_indices()

    indice = ler_opcao_inteira("Informe o índice do cadastro que receberá o novo insumo: ", 0, len(cadastros) - 1)

    cultura = cadastros[indice]["cultura"]
    novo_insumo = calcular_insumo(cultura)

    cadastros[indice]["manejo_insumos"].append(novo_insumo)
    print("\nNovo insumo adicionado com sucesso ao cadastro!")

def deletar_dados():
    print("\n==============================")
    print("       DELEÇÃO DE DADOS")
    print("==============================")

    if len(cadastros) == 0:
        print("Nenhum cadastro disponível para deleção.")
        return

    exibir_indices()

    indice = ler_opcao_inteira("Informe o índice do cadastro que deseja deletar: ", 0, len(cadastros) - 1)

    removido = cadastros.pop(indice)
    print(f"\nCadastro da fazenda '{removido['fazenda']}' removido com sucesso!")

def exportar_json():
    agora = datetime.now()
    nome_arquivo = agora.strftime("Dados cadastrados %d-%m-%Y - %H-%M.json")

    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
        json.dump(cadastros, arquivo, indent=4, ensure_ascii=False)

    print(f"\nArquivo '{nome_arquivo}' exportado com sucesso!")

def menu():
    while True:
        print("\n===================================")
        print(" SISTEMA FARMTECH SOLUTIONS")
        print("===================================")
        print("1 - Entrada de dados")
        print("2 - Saída de dados")
        print("3 - Atualização de dados")
        print("4 - Deleção de dados")
        print("5 - Adicionar insumo em cadastro existente")
        print("6 - Sair do programa E exportar dados cadastrados em arquivo .json na raiz do projeto")
        print("===================================")

        opcao = ler_opcao_inteira("Escolha uma opção: ", 1, 6)

        if opcao == 1:
            cadastrar_dados()
        elif opcao == 2:
            exibir_dados()
        elif opcao == 3:
            atualizar_dados()
        elif opcao == 4:
            deletar_dados()
        elif opcao == 5:
            adicionar_insumo_em_cadastro()
        elif opcao == 6:
            print("\nEncerrando o programa...")
            exportar_json()
            break

menu()