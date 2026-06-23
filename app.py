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
# ║  QR CODE PIX E ESTILOS SEGUROS                               ║
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

dados = carregar_dados()
config = dados["config"]
st.set_page_config(page_title=f"Lista {config['nome_casal']}", page_icon="🏠", layout="centered")

# CSS concatenado com parênteses (100% à prova de erro de sintaxe)
estilos_css = (
    "<style>"
    "h1, h2, h3, h4, h5, h6, p, label, .stMarkdown p { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important; }"
    ".stApp { background-color: #F4F7FA !important; color: #2D3748 !important; }"
    "#MainMenu, footer, header { visibility: hidden; }"
    ".stExpander { border: 2px solid #0B2545 !important; border-radius: 12px !important; background-color: #ffffff !important; box-shadow: 0 4px 12px rgba(11, 37, 69, 0.05) !important; margin-top: 20px !important; }"
    ".stExpander summary p { color: #0B2545 !important; font-weight: 700 !important; font-size: 1.1rem !important; }"
    "div[data-testid='stTabs'] button { color: #4A5568 !important; font-weight: 600 !important; font-size: 1rem !important; }"
    "div[data-testid='stTabs'] button[aria-selected='true'] { color: #0B2545 !important; border-bottom: 3px solid #0B2545 !important; font-weight: 700 !important; }"
    "code, pre { background-color: #F7FAFC !important; color: #0B2545 !important; font-family: monospace !important; font-size: 1rem !important; font-weight: 600 !important; border: 1px solid #CBD5E0 !important; }"
    "div[data-testid='stVerticalBlockBorderWrapper'] { border-radius: 16px !important; border: 1px solid #E2E8F0 !important; box-shadow: 0 8px 20px rgba(11, 37, 69, 0.03) !important; background-color: #ffffff !important; padding: 24px !important; margin-bottom: 15px !important; }"
    "div.stButton > button, div.stFormSubmitButton > button { background-color: #0B2545 !important; color: #ffffff !important; border: 1px solid #0B2545 !important; border-radius: 8px !important; padding: 10px 20px !important; font-weight: 600 !important; font-size: 0.95rem !important; width: 100% !important; transition: background 0.2s; }"
    "div.stButton > button:hover, div.stFormSubmitButton > button:hover { background-color: #134074 !important; border-color: #134074 !important; color: #ffffff !important; }"
    "label p { color: #0B2545 !important; font-weight: 600 !important; }"
    ".status-badge { padding: 6px 14px; border-radius: 30px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; display: inline-block; margin-top: 8px; }"
    ".disponivel { background-color: #EBF8FF; color: #2B6CB0; border: 1px solid #BEE3F8; }"
    ".pendente { background-color: #FEFCBF; color: #975A16; border: 1px solid #FEF08A; }"
    ".confirmado { background-color: #C6F6D5; color: #22543D; border: 1px solid #9AE6B4; }"
    ".img-container img { border-radius: 12px !important; object-fit: cover !important; }"
    "</style>"
)
st.markdown(estilos_css, unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════╗
# ║  MODAL DE PAGAMENTO                                          ║
# ╚══════════════════════════════════════════════════════════════╝

@st.dialog("🎁 Presentear")
def modal_presentear(item: dict, config: dict):
    st.markdown(f"<h2 style='color:#0B2545; font-weight:700; margin-top:0;'>{item['emoji']} {item['nome']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:1.1rem; color:#2D3748;'>Valor sugerido: <strong style='color:#0B2545; font-size:1.3rem;'>R$ {item['preco']:.2f}</strong></p>", unsafe_allow_html=True)
    
    payload = gerar_payload_pix(
        chave=config["chave_pix"],
        nome_beneficiario=config["nome_beneficiario"],
        cidade=config["cidade"],
        valor=item["preco"],
        descricao=item["id"][:25]
    )
    
    # HTML seguro
    html_instrucoes = (
        "<div style='background-color:#F7FAFC; padding:15px; border-radius:10px; font-size:0.95rem; margin-bottom:20px; border-left:4px solid #0B2545; color:#2D3748;'>"
        "<strong style='color:#0B2545;'>Como realizar o pagamento:</strong><br>"
        "1. Acesse o app do seu banco de preferência.<br>"
        "2. Escolha pagar via Pix, escaneie o QR Code ou utilize o Copia e Cola abaixo."
        "</div>"
    )
    st.markdown(html_instrucoes, unsafe_allow_html=True)
    
    col_qr, col_copy = st.
