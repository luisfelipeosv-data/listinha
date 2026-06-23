"""
Casinha Sara & Luis — Lista de Presentes 🏠
Estética Premium: Azul Escuro e Branco (Helvetica)
"""

import json
import io
import re
import threading
from datetime import datetime
from pathlib import Path
import streamlit as st
import qrcode

# ╔══════════════════════════════════════════════════════════════╗
# ║  CAMINHOS E CONSTANTES                                       ║
# ╚══════════════════════════════════════════════════════════════╝

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "catalogo.json"
SENHA_ADMIN = "casinha2026"

# Garantir que o diretório de dados existe
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

_file_lock = threading.Lock()

def _catalogo_padrao() -> dict:
    """Retorna estrutura inicial vazia com a sua chave Pix padrão."""
    return {
        "config": {
            "chave_pix": "8cc108fc-d117-4dcd-a080-9c6d0f9a1ca9",
            "tipo_chave": "aleatoria",
            "nome_casal": "Sara & Luis",
            "nome_beneficiario": "SARA E LUIS",
            "cidade": "SAO PAULO",
        },
        "itens": []  # Começa totalmente limpo
    }

def carregar_dados() -> dict:
    with _file_lock:
        if not DATA_FILE.exists():
            dados = _catalogo_padrao()
            DATA_FILE.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
            return dados
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            dados = _catalogo_padrao()
            DATA_FILE.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
            return dados

def salvar_dados(dados: dict) -> None:
    with _file_lock:
        DATA_FILE.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

def gerar_id(nome: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", nome.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return f"{slug}-{int(datetime.now().timestamp())}"

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
# ║  MODAL DE PAGAMENTO                                          ║
# ╚══════════════════════════════════════════════════════════════╝

@st.dialog("🎁 Presentear")
def modal_presentear(item: dict, config: dict):
    st.markdown(f"### {item['emoji']} {item['nome']}")
    st.markdown(f"Valor sugerido: <span style='color:#0B2545; font-weight:700;'>R$ {item['preco']:.2f}</span>", unsafe_allow_html=True)
    
    payload = gerar_payload_pix(
        chave=config["chave_pix"],
        nome_beneficiario=config["nome_beneficiario"],
        cidade=config["cidade"],
        valor=item["preco"],
        descricao=item["id"][:25]
    )
    
    st.markdown("""
    <div style='background-color:#f4f6f9; padding:15px; border-radius:10px; font-size:0.9rem; margin-bottom:15px; border-left:4px solid #0B2545;'>
        <strong>Como pagar:</strong><br>
        1. Abra o app do seu banco e escolha pagar via Pix (QR Code).<br>
        2. Escaneie o código abaixo ou copie o texto do "Copia e Cola".
    </div>
    """, unsafe_allow_html=True)
    
    col_qr, col_copy = st.columns([1, 1.2])
    with col_qr:
        st.image(gerar_qrcode_pix(payload), width=160)
    with col_copy:
        st.markdown("**Pix Copia e Cola:**")
        st.code(payload, language="text")
        
    st.divider()
    st.markdown("### Confirme seu Presente")
    
    with st.form(key=f"form_modal_{item['id']}"):
        nome_convidado = st.text_input("Seu nome:", placeholder="Ex: Ana Silva")
        if st.form_submit_button("Já fiz o Pix! Confirmar", use_container_width=True):
