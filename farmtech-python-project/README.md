# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# FarmTech Solutions - Agricultura Digital

## Nome do grupo
*Preencher nome do grupo*

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/in/jelielcardoso/">Jeliel Cardoso</a>
- <a href="https://www.linkedin.com/in/deise-n%C3%B3brega-159429163/">Deise Nobrega</a>
- <a href="https://www.linkedin.com/in/denispaulodiassilva/">Denis Paulo</a> 
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do integrante 4</a> 
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do integrante 5</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do Tutor</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do Coordenador</a>

## 📜 Descrição

Este projeto foi desenvolvido com o objetivo de simular uma aplicação de Agricultura Digital para uma fazenda que busca aumentar sua produtividade utilizando tecnologia.

A aplicação, desenvolvida em Python, permite o cadastro e gerenciamento de informações relacionadas ao plantio e manejo de insumos agrícolas, com foco nas culturas de café e milho.

O sistema possui funcionalidades para:

- Cadastro de fazendas, responsáveis e culturas
- Cálculo da área de plantio utilizando figuras geométricas (retângulo e triângulo)
- Cálculo do manejo de insumos com base em quantidade por metro, número de ruas e extensão da lavoura
- Armazenamento dos dados em estruturas de vetor (listas)
- Inserção de múltiplos insumos por cadastro
- Atualização seletiva de dados (sem necessidade de recadastro completo)
- Remoção de registros
- Exportação dos dados em formato JSON

O sistema foi desenvolvido utilizando conceitos fundamentais de programação, como estruturas de repetição, condicionais, manipulação de listas (vetores) e organização de dados em formato estruturado.

O objetivo principal é demonstrar, de forma prática, como soluções tecnológicas podem auxiliar na gestão agrícola e tomada de decisão.

## 📁 Estrutura de pastas

A estrutura do projeto é simples e contém apenas os arquivos essenciais:

- <b>main.py</b>: Arquivo principal contendo toda a lógica da aplicação.
- <b>README.md</b>: Documento com descrição do projeto e instruções de uso.
- <b>Dados cadastrados *.json</b>: Arquivos gerados automaticamente pelo sistema ao encerrar a aplicação, contendo os dados cadastrados.

## 🔧 Como executar o código

### Pré-requisitos

- Python 3.8 ou superior instalado
- Terminal (CMD, PowerShell, Bash ou terminal do VSCode)

### Verificar instalação do Python

python --version

ou

python3 --version

### Passo a passo para execução

1. Baixe ou clone o repositório:

git clone <url-do-repositorio>

2. Acesse a pasta do projeto:

cd nome-da-pasta

3. Execute o arquivo principal:

python main.py

ou

python3 main.py

### Uso do sistema

Ao executar o programa, será exibido um menu interativo com as opções:

- Entrada de dados (cadastro)
- Visualização dos dados
- Atualização de dados específicos
- Deleção de cadastros
- Adição de insumos em cadastros existentes
- Exportação dos dados para arquivo JSON ao sair

O arquivo JSON será gerado automaticamente na raiz do projeto com data e hora no nome.

## 🗃 Histórico de lançamentos

* 1.0.0 - XX/XX/2024
    * Versão inicial do sistema
    * Implementação de cadastro de culturas (café e milho)
    * Cálculo de área de plantio
    * Cálculo de manejo de insumos
    * Suporte a múltiplos insumos por cadastro
    * Atualização seletiva de dados
    * Deleção de registros
    * Exportação de dados em JSON

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
