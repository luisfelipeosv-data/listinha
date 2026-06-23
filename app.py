"""
Casinha Sara & Luis — Lista de Presentes Premium 🏠
Banco de Dados em Nuvem e Otimizado para Teclados de Celular
"""

import json
import io
import re
import base64
import streamlit as st
import qrcode

# ╔══════════════════════════════════════════════════════════════╗
# ║  CONEXÃO COM BANCO DE DADOS EM NUVEM (STREAMLIT SECRETS)     ║
# ╚══════════════════════════════════════════════════════════════╝

SENHA_ADMIN = "casinha2026"

try:
    conn = st.connection("kv", type="json")
except Exception:
    conn = None

def _catalogo_padrao() -> dict:
    return {
        "config": {
            "chave_pix": "8cc108fc-d117-4dcd-a080-9c6d0f9a1ca9",
            "tipo_chave": "aleatoria",
            "nome_casal": "Sara & Luis",
            "nome_beneficiario": "SARA E LUIS",
            "cidade": "SAO PAULO",
        },
        "itens": []
    }

def carregar_dados() -> dict:
    if "db_catalogo" not in st.session_state:
        if conn:
            dados = conn.get("catalogo_noivos")
            if not dados:
                dados = _catalogo_padrao()
                conn.set("catalogo_noivos", dados)
            st.session_state["db_catalogo"] = dados
        else:
            st.session_state["db_catalogo"] = _catalogo_padrao()
    return st.session_state["db_catalogo"]

def salvar_dados(dados: dict) -> None:
    st.session_state["db_catalogo"] = dados
    if conn:
        conn.set("catalogo_noivos", dados)

def gerar_id(nome: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", nome.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    import time
    return f"{slug}-{int(time.time())}"

# ╔══════════════════════════════════════════════════════════════╗
# ║  QR CODE PIX — Payload BR Code                               ║
# ╚══════════════════════════════════════════════════════════════╝

def _tlv(tag: str, valor: str) -> str:
    return f"{tag}{len(valor):02d}{valor}"

def _crc16_ccitt(payload: str) -> str:
    crc = 0xFFFF
    for byte in payload.encode("ascii"):
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return f"{crc:04X}"

def gerar_payload_pix(chave: str, nome_beneficiario: str, cidade: str, valor: float, descricao: str) -> str:
    gui = _tlv("00", "BR.GOV.BCB.PIX")
    chave_field = _tlv("01", chave)
    desc_field = _tlv("02", descricao[:25])
    mai = _tlv("26", gui + chave_field + desc_field)

    payload_parts = [
        _tlv("00", "01"),
        mai,
        _tlv("52", "0000"),
        _tlv("53", "986"),
    ]
    if valor > 0:
        payload_parts.append(_tlv("54", f"{valor:.2f}"))

    payload_parts.extend([
        _tlv("58", "BR"),
        _tlv("59", nome_beneficiario[:25].upper()),
        _tlv("60", cidade[:15].upper()),
        _tlv("62", _tlv("05", "***")),
    ])
    payload_sem_crc = "".join(payload_parts) + "6304"
    return payload_sem_crc + _crc16_ccitt(payload_sem_crc)

def gerar_qrcode_pix(payload: str) -> bytes:
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0B2545", back_color="#ffffff")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

# ╔══════════════════════════════════════════════════════════════╗
# ║  CONFIGURAÇÃO DA PÁGINA                                      ║
# ╚══════════════════════════════════════════════════════════════╝

dados = carregar_dados()
config = dados["config"]
st.set_page_config(page_title=f"Lista {config['nome_casal']}", page_icon="🏠", layout="centered")

# Estilos Visuais Ajustados
st.markdown("""
<style>
h1, h2, h3, h4, h5, h6, p, label, .stMarkdown p {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
}
.stApp { 
    background-color: #F4F7FA !important;
    color: #2D3748 !important; 
}
#MainMenu, footer, header { visibility: hidden; }

.stExpander {
    border: 2px solid #0B2545 !important;
    border-radius: 12px !important;
    background-color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(11, 37, 69, 0.05) !important;
    margin-top: 20px !important;
}
.stExpander summary p {
    color: #0B2545 !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
}

div[data-testid="stTabs"] button {
    color: #4A5568 !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #0B2545 !important;
    border-bottom: 3px solid #0B
