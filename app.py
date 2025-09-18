from dataclasses import dataclass
import csv
import os
import requests
from datetime import datetime
from typing import List, Optional
import streamlit as st
import pandas as pd
from produto import Produto
from venda import Venda
from cliente import Cliente

PRODUTOS_FILE = "produtos.txt"
VENDAS_FILE = "vendas.txt"
CLIENTES_FILE = "clientes.txt"

HEADERS_PRODUTOS = ["Nome", "Preco", "quantidade"]
HEADERS_VENDAS = ["Data_iso", "Produto", "Quantidade", "Valor_total", "CPF-cliente"]
HEADERS_CLIENTES = ["CPF", "nome", "datanascimento", "endereço", "telefone" ]  

def ensure_files() -> None:
    if not os.path.exists(PRODUTOS_FILE):
        with open(PRODUTOS_FILE, "w", newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(HEADERS_PRODUTOS)
    if not os.path.exists(VENDAS_FILE):
        with open(VENDAS_FILE, "w", newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(HEADERS_VENDAS)
    if not os.path.exists(CLIENTES_FILE):
        with open(CLIENTES_FILE, "w", newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(HEADERS_CLIENTES)

def carregar_produtos() -> list[Produto]:
    produtos: List[Produto] = []
    if not os.path.exists(PRODUTOS_FILE):
        return produtos
    with open(PRODUTOS_FILE, "r", newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) == 3:
                try:
                    produtos.append(Produto.from_row(row))
                except ValueError:
                    continue
    return produtos
def salvar_produtos(produtos: list[Produto]) -> None:
    with open(PRODUTOS_FILE, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS_PRODUTOS)
        writer.writerows([p.to_row() for p in produtos])

def carregar_vendas() -> list[Venda]:
    vendas: List[Venda] = []
    if not os.path.exists(VENDAS_FILE):
        return vendas
    with open(VENDAS_FILE, "r", newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) == 4:
                try:
                    vendas.append(Venda.from_row(row))
                except ValueError:
                    continue
    return vendas

def registrarvendaarquivo(venda: Venda) -> None:
    with open(VENDAS_FILE, "a", newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(venda.to_row())

def carregar_clientes() -> list[Cliente]:
    clientes: List[Cliente] = []
    if not os.path.exists(CLIENTES_FILE):
        return clientes
    with open(CLIENTES_FILE, "r", newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) == 5:
                    clientes.append(Cliente.from_row(row))
    return clientes

def salvar_clientes(clientes: list[Cliente]) -> None:
    with open(CLIENTES_FILE, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS_CLIENTES)
        writer.writerows([c.to_row() for c in clientes])

ensure_files()

@st.cache_data
def get_produtos() -> list[Produto]:
    return carregar_produtos()
@st.cache_data
def get_vendas() -> list[Venda]:
    return carregar_vendas()
@st.cache_data
def get_clientes() -> list[Cliente]:
    return carregar_clientes()

st.set_page_config(page_title="Controle de estoque", layout="wide")
st.title(" Sistema de controle de estoque")

menu = st.sidebar.radio("Navegação", ["cadastro de produtos", "cadastro de clientes", "registro de vendas", "relatórios"])

if menu == "cadastro de produtos":
    st.header("Cadastro de produtos")
    produtos = get_produtos()

    with st.form("form_cadastro", clear_on_submit=True):
        nome = st.text_input("Nome do produto")
        preco = st.number_input("Preço R$", min_value=0.0, format="%.2f", step=0.50)
        quantidade = st.number_input("Quantidade inicial", min_value=0, step=1, value=1)
        submitted = st.form_submit_button("Salvar produto")
    if submitted:
        if not nome.strip():
            st.warning("informe o nome do produto.")
        else:
            nome = nome.strip()
            existente: Optional[Produto] = next((p for p in produtos if p.nome.lower() == nome.lower()), None)
            if existente:
                existente.quantidade += int (quantidade)
                existente.preco = float(preco)
                st.success(f"Produto '{nome}' atualizado.")
            else:
                produtos.append(Produto(nome, float(preco), int(quantidade)))
                st.success(f"Produto '{nome}' cadastro com sucesso.")
            salvar_produtos(produtos)
            st.cache_data.clear()
    st.subheader(" ✔️ Produtos cadastrados")
    if produtos:
        df = [{"Nome": p.nome, "Preço R$": f"{p.preco:.2f}", "Quantidade": p.quantidade} for p in produtos]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado ainda.")
        
elif menu == "cadastro de clientes":
    st.header("Cadastro de clientes")
    clientes = get_clientes()

    with st.form("form_clientes", clear_on_submit=True):
        cpf = st.text_input("CPF")
        nome = st.text_input("Nome completo")
        datanascimento = st.date_input("Data de nascimento")
        cep = st.text_input("CEP")
        telefone = st.text_input("telefone")
        endereco = ""
        buscar = st.form_submit_button("Buscar endereço pelo CEP")
        if buscar and cep.strip():
            try:
                resp = requests.get(f"https://brasilapi.com.br/api/cep/v1/{cep.strip()}")
                if resp.status_code == 200:
                    data = resp.json()
                    endereco = f"{data['street']}, {data['neighborhood']}, {data['city']} - {data['state']}"
                    st.success(f"Endereço encontrado: {endereco}") 
                else:
                    st.warning("CEP não encontrado, coloque manualmente.")
                    endereco = st.text_input("Endereço completo")
            except:
                st.error("Erro ao consyltar o CEP")
                endereco = st.text_input("Endereço completo")
        submitted = st.form_submit_button("Salvar cliente")
    if submitted:
        if not cpf.strip() or not nome.strip():
            st.warning("Informe pelo menos o CPF e nome.")
        else:
            clientes.append(Cliente(cpf.strip(), nome.strip(), str(datanascimento),endereco.strip() if endereco else cep.strip(), telefone.strip()))
            salvar_clientes(clientes)
            st.cache_data.clear()
            st.success(f"Cliente '{nome}' cadastrado com sucesso.")
    st.subheader(" Clientes cadastrados")
    if clientes:
        df =[{"CPF": c.cpf, "Nome": c.nome, "telefone": c.telefone} for c in clientes]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("nenhum cliente cadastrado ainda.")
              

elif menu == "registro de vendas":
    st.header("Registro de vendas")
    produtos = get_produtos()
    vendas = get_vendas()
    clientes = get_clientes()

    if not produtos:
        st.warning(" ❌ Nenhum produto cadastrado")  
    elif not clientes:
        st.warning(" ❌ Nenhum cliente cadastrado")
    else:
        with st.form("form_vendas", clear_on_submit=True):
            cpf_cliente = st.selectbox("Cliente (CPF)", [c.cpf for c in clientes])
            produto_escolhido = st.selectbox("Produto", [p.nome for p in produtos])
            prod_obj = next(p for p in produtos if p.nome == produto_escolhido)  
            st.write(f"Preço unitario: R$ {prod_obj.preco:.2f} | Estoque atual: {prod_obj.quantidade}")
            quantidade_vendida = st.number_input("Quantidade vendida", min_value=1, step=1, value=1)
            confirmar = st.form_submit_button("registrar venda")

        if confirmar:
            if quantidade_vendida > prod_obj.quantidade:
                st.error(f"Quantidade indisponivel. Estoque atual: {prod_obj.quantidade}.")
            else:
                valor_total = round(prod_obj.preco * quantidade_vendida, 2)
                venda = Venda(datetime.now(), prod_obj.nome, int(quantidade_vendida), valor_total)
                prod_obj.quantidade -= int(quantidade_vendida)
                salvar_produtos(produtos)
                registrarvendaarquivo(venda)
                st.cache_data.clear()

                st.success(f"Venda registrada: {venda.quantidade} x {venda.valor_total:.2f}")
                st.info(f"Estoque restante de '{prod_obj.nome}': {prod_obj.quantidade}")

elif menu == "relatórios":
    st.header(" 📄 Relatórios")

    produtos = get_produtos()
    vendas = get_vendas()

    st.subheader("Produtos")
    if produtos: 
        df = [{"Nome": p.nome, "Preço R$": f"{p.preco:.2f}", "Quantidade": p.quantidade} for p in produtos]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado.")
    st.subheader("Histórico de vendas")
    if vendas:
        vendasordenadas = sorted(vendas, key=lambda v: v.data_iso, reverse=True)
        df_vendas = [
            {
                "Data": v.data_iso.strftime("%Y-%m-%d %H:%M:%S"),
                "Produto": v.produto,
                "Quantidade": v.quantidade,
                "Valor total R$": f"{v.valor_total:.2f}"
            }
            for v in vendasordenadas
        ]
        receitatotal = sum(v.valor_total for v in vendas)
        st.dataframe(df_vendas, use_container_width=True)
        st.markdown(f"Receita total: R$ {receitatotal:.2f}")
    else: 
        st.info("Ainda nao há vendas registradas.")
    st.subheader(" ⬇️ Estoque baixo")
    estoquemin = 5
    produtosbx = [p for p in produtos if p.quantidade <= estoquemin]
    
    if produtosbx:
        dfalerta = [{"Nome": p.nome, "Quantidade": p.quantidade} for p in produtosbx]
        st.warning("Alguns produtos estão com estoque baixo")
        st.table(dfalerta)
    else:
        st.info(" ❌ Nenhum produto com estoque baixo.")

    if produtos:
        df_produtos = pd.DataFrame([{"Nome": p.nome, "Quantidade":p.quantidade} for p in produtos])
        st.subheader("Estoque atual por produto")
        st.bar_chart(df_produtos.set_index("Nome")["Quantidade"])
    if vendas:
        df_vendas_graf = pd.DataFrame([{"Data": v.data_iso, "Valor total": v.valor_total} for v in vendas])
        df_vendas_graf["Data"] = pd.to_datetime(df_vendas_graf["Data"])
        vendapord = df_vendas_graf.groupby(df_vendas_graf["Data"].dt.date)["Valor total"].sum().reset_index()
        vendapord.set_index("Data", inplace=True)

        st.subheader(" 📈 Evolução das vendas")
        st.line_chart(vendapord)
    st.markdown("---")
    st.caption(f"Arquivos persistente: '{PRODUTOS_FILE}', '{VENDAS_FILE}' ")

