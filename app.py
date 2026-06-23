import json
import io
import re
import base64
import os
import streamlit as st
import qrcode
import requests
import unicodedata

# ╔══════════════════════════════════════════════════════════════╗
# ║  SISTEMA DE BANCO DE DADOS LOCAL (IMUNIZADO CONTRA REFRESH)  ║
# ╚══════════════════════════════════════════════════════════════╝

SENHA_ADMIN = "casinha2026"
ARQUIVO_BANCO = "banco_presentes.json"

def _catalogo_padrao() -> dict:
    return {
        "config": {
            "chave_pix": "8cc108fc-d117-4dcd-a080-9c6d0f9a1ca9",
            "tipo_chave": "aleatoria",
            "nome_casal": "Sara & Luis",
            "nome_beneficiario": "SARA E LUIS",
            "cidade": "SAO PAULO",
            "mp_access_token": ""
        },
        "itens": []
    }

def carregar_dados() -> dict:
    if os.path.exists(ARQUIVO_BANCO):
        try:
            with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if "mp_access_token" not in dados["config"]:
                    dados["config"]["mp_access_token"] = ""
                st.session_state["db_catalogo"] = dados
                return dados
        except Exception:
            pass
            
    if "db_catalogo" not in st.session_state:
        st.session_state["db_catalogo"] = _catalogo_padrao()
        with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
            json.dump(st.session_state["db_catalogo"], f, ensure_ascii=False, indent=4)
            
    return st.session_state["db_catalogo"]

def salvar_dados(dados: dict) -> None:
    st.session_state["db_catalogo"] = dados
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def remover_acentos(texto: str) -> str:
    """ Remove acentos e caracteres especiais para blindar o Pix e IDs """
    if not texto:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def gerar_id(nome: str) -> str:
    nome_limpo = remover_acentos(nome.lower())
    slug = re.sub(r"[^\w\s-]", "", nome_limpo)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    import time
    return f"{slug}-{int(time.time())}"

# ╔══════════════════════════════════════════════════════════════╗
# ║  INTEGRAÇÃO MERCADO PAGO (COM DIAGNÓSTICO DE ERROS ATIVO)    ║
# ╚══════════════════════════════════════════════════════════════╝

def gerar_link_cartao_mercado_pago(item: dict, access_token: str) -> str:
    if not access_token or access_token.strip() == "":
        st.warning("⚠️ O Token do Mercado Pago está vazio ou não foi carregado corretamente.")
        return None
        
    url = "https://api.mercadopago.com/v1/preferences"
    headers = {
        "Authorization": f"Bearer {access_token.strip()}",
        "Content-Type": "application/json"
    }
    
    titulo_produto = remover_acentos(f"Presente: {item['emoji']} {item['nome']}")
    
    payload = {
        "items": [
            {
                "title": titulo_produto[:256],
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(item["preco"])
            }
        ],
        "payment_methods": {
            "excluded_payment_types": [
                {"id": "ticket"},        
                {"id": "bank_transfer"}  
            ],
            "installments": 12           
        },
        "auto_return": "approved"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            return response.json().get("init_
