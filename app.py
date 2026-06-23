"""
Casinha Sara & Luis — Lista de Presentes 🏠
Streamlit app para chá de casa nova.
Deploy: Streamlit Community Cloud via GitHub.

Features:
- Catálogo de presentes com fotos e QR Code PIX
- Painel CRUD para admin gerenciar itens
- Notificação por email (opcional)
- Design premium com responsividade mobile
"""

import json
import os
import io
import re
import smtplib
import threading
import struct
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path

import streamlit as st
import qrcode
from PIL import Image
import pandas as pd

# ╔══════════════════════════════════════════════════════════════╗
# ║  CAMINHOS E CONSTANTES                                      ║
# ╚══════════════════════════════════════════════════════════════╝

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "catalogo.json"
UPLOAD_DIR = BASE_DIR / "uploads"
SENHA_ADMIN = "casinha2026"

# Garantir que diretórios existem
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


# ╔══════════════════════════════════════════════════════════════╗
# ║  PERSISTÊNCIA (JSON)                                        ║
# ╚══════════════════════════════════════════════════════════════╝

_file_lock = threading.Lock()


def _catalogo_padrao() -> dict:
    """Retorna catálogo padrão caso o JSON não exista."""
    return {
        "config": {
            "chave_pix": "suachavepix@email.com",
            "tipo_chave": "email",
            "nome_casal": "Sara & Luis",
            "nome_beneficiario": "SARA E LUIS",
            "cidade": "SAO PAULO",
        },
        "itens": [
            {"id": "air-fryer-digital", "nome": "Air Fryer Digital", "preco": 350.0, "emoji": "🍳", "desc": "Refeições práticas e saudáveis", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "jogo-de-panelas", "nome": "Jogo de Panelas", "preco": 250.0, "emoji": "🍲", "desc": "Base da nossa cozinha", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "jogo-de-cama-casal", "nome": "Jogo de Cama Casal", "preco": 200.0, "emoji": "🛏️", "desc": "Conforto para as noites", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "jogo-de-toalhas", "nome": "Jogo de Toalhas", "preco": 150.0, "emoji": "🛁", "desc": "Banho quentinho todo dia", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "cafeteira-eletrica", "nome": "Cafeteira Elétrica", "preco": 180.0, "emoji": "☕", "desc": "Café fresquinho toda manhã", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "liquidificador", "nome": "Liquidificador", "preco": 120.0, "emoji": "🥤", "desc": "Sucos, vitaminas e sopas", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "aspirador-de-po", "nome": "Aspirador de Pó", "preco": 400.0, "emoji": "🧹", "desc": "Casa sempre limpinha", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "ferro-de-passar", "nome": "Ferro de Passar", "preco": 100.0, "emoji": "👔", "desc": "Roupas sempre alinhadas", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "jogo-de-talheres-24pc", "nome": "Jogo de Talheres 24pç", "preco": 130.0, "emoji": "🍴", "desc": "Para receber a família", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "aparelho-de-jantar", "nome": "Aparelho de Jantar", "preco": 220.0, "emoji": "🍽️", "desc": "Jantares especiais em casa", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "micro-ondas", "nome": "Micro-ondas", "preco": 450.0, "emoji": "📡", "desc": "Praticidade no dia a dia", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "kit-churrasco", "nome": "Kit Churrasco", "preco": 160.0, "emoji": "🥩", "desc": "Domingos em família", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "ventilador-de-coluna", "nome": "Ventilador de Coluna", "preco": 200.0, "emoji": "🌀", "desc": "Brisa nos dias quentes", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "escorredor-de-louca", "nome": "Escorredor de Louça", "preco": 80.0, "emoji": "🫧", "desc": "Organização na cozinha", "foto": None, "status": "disponivel", "quem": ""},
            {"id": "lixeira-automatica", "nome": "Lixeira Automática", "preco": 90.0, "emoji": "🗑️", "desc": "Toque moderno na cozinha", "foto": None, "status": "disponivel", "quem": ""},
        ],
    }


def carregar_dados_locais() -> dict:
    """Carrega dados do JSON local. Cria arquivo padrão se não existir."""
    with _file_lock:
        if not DATA_FILE.exists():
            dados = _catalogo_padrao()
            DATA_FILE.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
            return dados
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            dados = _catalogo_padrao()
            DATA_FILE.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
            return dados


def salvar_dados_locais(dados: dict) -> None:
    """Salva dados no JSON local de forma thread-safe."""
    with _file_lock:
        DATA_FILE.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def carregar_dados() -> dict:
    """Carrega dados da planilha do Google Sheets com fallback para o JSON local."""
    # Verificar se as secrets do gsheets estão configuradas
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        try:
            from streamlit_gsheets import GSheetsConnection
            conn = st.connection("gsheets", type=GSheetsConnection)
            
            # 1. Carregar Configurações
            df_config = conn.read(worksheet="config", ttl="0d")
            config = dict(zip(df_config["chave"], df_config["valor"]))
            
            # 2. Carregar Itens
            df_itens = conn.read(worksheet="itens", ttl="0d")
            # Garantir tipos de dados corretos e tratar nulos
            df_itens["preco"] = pd.to_numeric(df_itens["preco"], errors="coerce").fillna(0.0)
            df_itens["foto"] = df_itens["foto"].fillna("")
            df_itens["quem"] = df_itens["quem"].fillna("")
            df_itens["emoji"] = df_itens["emoji"].fillna("🎁")
            df_itens["desc"] = df_itens["desc"].fillna("")
            df_itens["status"] = df_itens["status"].fillna("disponivel")
            
            itens = df_itens.to_dict(orient="records")
            return {
                "config": config,
                "itens": itens
            }
        except Exception as e:
            st.sidebar.warning(f"⚠️ Google Sheets inacessível ({e}). Usando base local.")
            return carregar_dados_locais()
    else:
        return carregar_dados_locais()


def salvar_dados(dados: dict) -> None:
    """Salva dados na planilha do Google Sheets com fallback para o JSON local."""
    # Sempre salva localmente como backup/redundância
    salvar_dados_locais(dados)
    
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        try:
            from streamlit_gsheets import GSheetsConnection
            conn = st.connection("gsheets", type=GSheetsConnection)
            
            # 1. Atualizar aba de configurações
            df_config = pd.DataFrame(list(dados["config"].items()), columns=["chave", "valor"])
            conn.update(worksheet="config", data=df_config)
            
            # 2. Atualizar aba de itens
            df_itens = pd.DataFrame(dados["itens"])
            conn.update(worksheet="itens", data=df_itens)
        except Exception as e:
            st.error(f"Erro ao salvar no Google Sheets: {e}")


def gerar_id(nome: str) -> str:
    """Gera ID slug a partir do nome."""
    slug = re.sub(r"[^\w\s-]", "", nome.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug


def otimizar_e_salvar_imagem(upload_file, output_path) -> str:
    """Abre a imagem enviada, recorta/redimensiona para formato padrão quadrado e salva em WebP."""
    try:
        img = Image.open(upload_file)
        
        # Converter para RGB para garantir compatibilidade ao salvar como WebP
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # Redimensionar e cortar para fazer um quadrado perfeito (ex: 400x400)
        largura, altura = img.size
        tamanho_alvo = min(largura, altura)
        
        # Crop centralizado
        esquerda = (largura - tamanho_alvo) / 2
        superior = (altura - tamanho_alvo) / 2
        direita = (largura + tamanho_alvo) / 2
        inferior = (altura + tamanho_alvo) / 2
        
        img_cropped = img.crop((esquerda, superior, direita, inferior))
        
        # Redimensiona para 400x400
        img_resized = img_cropped.resize((400, 400), Image.Resampling.LANCZOS)
        
        # Salva como WEBP (muito leve)
        img_resized.save(output_path, "WEBP", quality=85)
        return output_path.name
    except Exception as e:
        # Se falhar por algum motivo de biblioteca, salva o arquivo original
        output_path.write_bytes(upload_file.getbuffer())
        return output_path.name



# ╔══════════════════════════════════════════════════════════════╗
# ║  QR CODE PIX — Payload BR Code (Banco Central)             ║
# ╚══════════════════════════════════════════════════════════════╝

def _tlv(tag: str, valor: str) -> str:
    """Formata um campo TLV (Tag-Length-Value) para o BR Code."""
    return f"{tag}{len(valor):02d}{valor}"


def _crc16_ccitt(payload: str) -> str:
    """Calcula CRC16-CCITT (0xFFFF) conforme especificação BR Code."""
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


def gerar_payload_pix(
    chave: str,
    nome_beneficiario: str = "SARA E LUIS",
    cidade: str = "SAO PAULO",
    valor: float | None = None,
    descricao: str = "",
) -> str:
    """Gera payload PIX estático no formato BR Code do Banco Central."""
    # Merchant Account Information (ID 26)
    gui = _tlv("00", "BR.GOV.BCB.PIX")
    chave_field = _tlv("01", chave)
    if descricao:
        desc_field = _tlv("02", descricao[:25])
        mai = _tlv("26", gui + chave_field + desc_field)
    else:
        mai = _tlv("26", gui + chave_field)

    # Campos obrigatórios
    payload_parts = [
        _tlv("00", "01"),           # Payload Format Indicator
        mai,                         # Merchant Account Information
        _tlv("52", "0000"),         # Merchant Category Code
        _tlv("53", "986"),          # Transaction Currency (BRL)
    ]

    # Valor (opcional)
    if valor and valor > 0:
        valor_str = f"{valor:.2f}"
        payload_parts.append(_tlv("54", valor_str))

    payload_parts.extend([
        _tlv("58", "BR"),                                    # Country Code
        _tlv("59", nome_beneficiario[:25].upper()),          # Merchant Name
        _tlv("60", cidade[:15].upper()),                     # Merchant City
        _tlv("62", _tlv("05", "***")),                       # Additional Data
    ])

    # Montar payload sem CRC
    payload_sem_crc = "".join(payload_parts) + "6304"

    # Calcular e anexar CRC16
    crc = _crc16_ccitt(payload_sem_crc)
    return payload_sem_crc + crc


def gerar_qrcode_pix(payload: str) -> bytes:
    """Gera imagem PNG do QR Code a partir do payload PIX."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#2c2c2c", back_color="#ffffff")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


# ╔══════════════════════════════════════════════════════════════╗
# ║  NOTIFICAÇÃO POR EMAIL                                      ║
# ╚══════════════════════════════════════════════════════════════╝

def enviar_email_notificacao(presente: str, valor: float, quem: str) -> bool:
    """Envia email de notificação ao casal. Retorna True se enviou."""
    try:
        email_cfg = st.secrets.get("email", {})
        if not email_cfg.get("ativar", False):
            return False

        corpo = f"""🎁 Novo presente na lista!

Presente: {presente}
Valor: R$ {valor:.2f}
De: {quem}
Data: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

Acesse o painel de administração para confirmar o recebimento.
"""
        msg = MIMEText(corpo, "plain", "utf-8")
        msg["Subject"] = f"🏠 Casinha — {quem} quer presentear: {presente}"
        msg["From"] = email_cfg["sender_email"]
        msg["To"] = email_cfg["receiver_email"]

        with smtplib.SMTP(email_cfg["smtp_server"], int(email_cfg["smtp_port"])) as server:
            server.starttls()
            server.login(email_cfg["sender_email"], email_cfg["app_password"])
            server.sendmail(msg["From"], msg["To"], msg.as_string())
        return True
    except Exception:
        # Falha silenciosa — não travar o app por causa de email
        return False


@st.dialog("🎁 Confirmar Presente")
def modal_presentear(item: dict, config: dict):
    st.markdown(f"### {item['emoji']} {item['nome']}")
    st.markdown(f"Valor sugerido: <span class='preco'>R$ {item['preco']:.2f}</span>", unsafe_allow_html=True)
    
    # Gerar payload e QR Code
    payload = gerar_payload_pix(
        chave=config["chave_pix"],
        nome_beneficiario=config.get("nome_beneficiario", "SARA E LUIS"),
        cidade=config.get("cidade", "SAO PAULO"),
        valor=item["preco"],
        descricao=item["id"][:25],
    )
    
    st.markdown(
        '<div class="pix-instrucao">'
        '<strong>Como realizar o pagamento:</strong><br>'
        '1. Abra o app do seu banco e selecione a opção de pagar via Pix (QR Code).<br>'
        '2. Aponte a câmera para o QR Code abaixo.<br>'
        '3. Se preferir, copie e cole o código Pix abaixo.'
        '</div>',
        unsafe_allow_html=True,
    )
    
    qr_bytes = gerar_qrcode_pix(payload)
    
    col_qr, col_copy = st.columns([1, 1.2])
    with col_qr:
        st.image(qr_bytes, caption="Escaneie para pagar", width=180)
    with col_copy:
        st.markdown("**Pix Copia e Cola:**")
        st.code(payload, language="text")
        st.caption("Toque duas vezes no código para copiar")
        
    st.divider()
    st.markdown("### ✍️ Confirmação do Presente")
    st.markdown("Depois de realizar a transferência, preencha seu nome para podermos dar baixa no presente:")
    
    with st.form(key=f"form_modal_{item['id']}"):
        nome_convidado = st.text_input(
            "Seu nome:",
            placeholder="Ex: Maria Souza",
            help="Se preferir, deixe em branco para enviar de forma anônima"
        )
        enviado = st.form_submit_button("✅ Já enviei o Pix! Confirmar presente", use_container_width=True)
        
        if enviado:
            quem = nome_convidado.strip() or "Anônimo"
            
            # Atualizar status no JSON
            dados_atuais = carregar_dados()
            for i, it in enumerate(dados_atuais["itens"]):
                if it["id"] == item["id"]:
                    dados_atuais["itens"][i]["status"] = "pendente"
                    dados_atuais["itens"][i]["quem"] = quem
                    break
            salvar_dados(dados_atuais)
            
            # Enviar e-mail de notificação em segundo plano
            threading.Thread(
                target=enviar_email_notificacao,
                args=(item["nome"], item["preco"], quem),
                daemon=True,
            ).start()
            
            st.success(f"Obrigado, {quem}! O status do presente foi atualizado para aguardando confirmação. 💛")
            st.balloons()
            st.toast(f"Obrigado, {quem}! Notificação enviada para {config['nome_casal']}.")
            st.rerun()


# ╔══════════════════════════════════════════════════════════════╗
# ║  CONFIGURAÇÃO DA PÁGINA                                     ║
# ╚══════════════════════════════════════════════════════════════╝


dados = carregar_dados()
config = dados["config"]
NOME_CASAL = config["nome_casal"]

st.set_page_config(
    page_title=f"Casinha {NOME_CASAL}",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ╔══════════════════════════════════════════════════════════════╗
# ║  CSS PREMIUM                                                ║
# ╚══════════════════════════════════════════════════════════════╝

st.markdown("""
<style>
/* ---------- Google Fonts ---------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');

/* ---------- Base ---------- */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: linear-gradient(160deg, #fdfaf6 0%, #faf5ee 30%, #f7f0e8 60%, #f5ebe0 100%);
}

/* ---------- Esconder elementos Streamlit ---------- */
#MainMenu, footer, header {visibility: hidden;}
[data-testid="stStatusWidget"] {display: none;}

/* ---------- Containers / Cards ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
    border-color: rgba(192, 130, 90, 0.08) !important;
    box-shadow:
        0 1px 3px rgba(0, 0, 0, 0.03),
        0 4px 16px rgba(192, 130, 90, 0.06);
    transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1),
                box-shadow 0.3s ease;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-3px);
    box-shadow:
        0 4px 12px rgba(0, 0, 0, 0.04),
        0 8px 32px rgba(192, 130, 90, 0.1);
}

/* ---------- Botões ---------- */
.stButton > button {
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.88rem;
    letter-spacing: 0.02em;
    padding: 0.5rem 1.4rem;
    transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
    border: none;
}

.stButton > button[kind="primary"],
.stButton > button:first-of-type {
    background: linear-gradient(135deg, #c0825a 0%, #b3724c 50%, #a86e4a 100%);
    color: white;
    box-shadow: 0 2px 8px rgba(192, 130, 90, 0.3);
}

.stButton > button[kind="primary"]:hover,
.stButton > button:first-of-type:hover {
    background: linear-gradient(135deg, #a86e4a 0%, #96603f 50%, #8d5b3b 100%);
    transform: translateY(-1px) scale(1.02);
    box-shadow: 0 4px 16px rgba(192, 130, 90, 0.4);
}

.stButton > button:active {
    transform: translateY(0) scale(0.98);
}

/* ---------- Formulários ---------- */
[data-testid="stForm"] {
    border: 1.5px dashed rgba(192, 130, 90, 0.2) !important;
    border-radius: 16px !important;
    background: rgba(255, 252, 247, 0.9) !important;
    backdrop-filter: blur(8px);
}

/* ---------- Inputs ---------- */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    border-radius: 10px !important;
    border-color: rgba(192, 130, 90, 0.15) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: #c0825a !important;
    box-shadow: 0 0 0 2px rgba(192, 130, 90, 0.15) !important;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1e1e 0%, #2c2c2c 50%, #1e1e1e 100%);
}

[data-testid="stSidebar"] * {
    color: #e8e8e8;
}

[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input,
[data-testid="stSidebar"] .stTextArea textarea {
    background: #3a3a3a;
    border-color: #555;
    color: #fff;
}

[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #3a3a3a;
    border-color: #555;
    color: #fff;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: none;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:hover {
    background: rgba(255, 255, 255, 0.08);
    transform: none;
}

/* ---------- Divider ---------- */
hr {
    border-color: rgba(192, 130, 90, 0.08) !important;
    margin: 0.5rem 0 !important;
}

/* ---------- Code block (PIX) ---------- */
[data-testid="stCode"] {
    border-radius: 12px;
    font-size: 0.85rem;
}

/* ---------- Badges personalizados ---------- */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.3rem 0.85rem;
    border-radius: 24px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.badge-disponivel {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    color: #2e7d32;
}

.badge-pendente {
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    color: #e65100;
    animation: pulse-badge 2s ease-in-out infinite;
}

.badge-confirmado {
    background: linear-gradient(135deg, #ede7f6, #d1c4e9);
    color: #5e35b1;
}

@keyframes pulse-badge {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.7; }
}

/* ---------- Hero ---------- */
.hero-section {
    text-align: center;
    padding: 2rem 1rem 1rem;
    position: relative;
}

.hero-section .icon {
    font-size: 4rem;
    margin-bottom: 0.5rem;
    animation: float 3s ease-in-out infinite;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
}

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-10px); }
}

.hero-section h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #2c2c2c 0%, #c0825a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem;
    line-height: 1.2;
}

.hero-section p {
    font-size: 1.05rem;
    color: #888;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.7;
    font-weight: 300;
}

/* ---------- Decoração Hero ---------- */
.hero-decor {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 0.8rem;
    font-size: 0.9rem;
    opacity: 0.5;
}

/* ---------- Barra de Progresso ---------- */
.progress-container {
    max-width: 480px;
    margin: 0.5rem auto 0;
    padding: 0 1rem;
}

.progress-bar-bg {
    background: rgba(192, 130, 90, 0.1);
    border-radius: 20px;
    height: 10px;
    overflow: hidden;
    position: relative;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 20px;
    background: linear-gradient(90deg, #c0825a 0%, #d4a574 50%, #e8c8a0 100%);
    transition: width 1s cubic-bezier(0.34, 1.56, 0.64, 1);
    position: relative;
}

.progress-bar-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    animation: shimmer 2s ease-in-out infinite;
}

@keyframes shimmer {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.progress-text {
    text-align: center;
    font-size: 0.82rem;
    color: #999;
    margin-top: 0.4rem;
    font-weight: 500;
}

/* ---------- Item emoji ---------- */
.item-emoji {
    font-size: 3.5rem;
    height: 180px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #fffcf7, #fdf5ea);
    border-radius: 12px;
    margin-bottom: 0.8rem;
    border: 1px dashed rgba(192, 130, 90, 0.15);
}

/* ---------- Foto do item ---------- */
.item-foto-container {
    width: 100%;
    height: 180px;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 0.8rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.item-foto-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* ---------- Grid Item Classes ---------- */
.card-content {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 0.2rem;
}

.card-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #2c2c2c;
    margin: 0.2rem 0 0.1rem 0;
    line-height: 1.3;
}

.card-desc {
    font-size: 0.85rem;
    color: #777;
    margin-bottom: 0.8rem;
    line-height: 1.4;
    min-height: 2.8em;
}

.card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: auto;
    padding-top: 0.5rem;
}

/* ---------- Preço ---------- */
.preco {
    color: #c0825a;
    font-weight: 700;
    font-size: 1.1rem;
}

/* ---------- Stats Row ---------- */
.stats-row {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    padding: 0.5rem 0 1rem;
}

.stat {
    text-align: center;
}

.stat .number {
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #c0825a, #d4a574);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat .label {
    font-size: 0.72rem;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}

/* ---------- QR Code container ---------- */
.qr-container {
    text-align: center;
    padding: 1rem;
}

.qr-container img {
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

/* ---------- PIX section ---------- */
.pix-instrucao {
    background: linear-gradient(135deg, #fff9f2, #fff4e6);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    border-left: 3px solid #c0825a;
    font-size: 0.9rem;
    line-height: 1.6;
}

/* ---------- Footer ---------- */
.footer {
    text-align: center;
    padding: 3rem 1rem 1.5rem;
    color: #ccc;
    font-size: 0.82rem;
    font-weight: 300;
}

.footer a {
    color: #c0825a;
    text-decoration: none;
}

/* ---------- Admin badge ---------- */
.admin-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.15rem 0.5rem;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.admin-badge-disponivel { background: #1b5e20; color: #a5d6a7; }
.admin-badge-pendente   { background: #e65100; color: #ffe0b2; }
.admin-badge-confirmado { background: #4527a0; color: #d1c4e9; }

/* ---------- Responsividade Mobile ---------- */
@media (max-width: 768px) {
    .hero-section h1 {
        font-size: 1.8rem;
    }

    .hero-section p {
        font-size: 0.95rem;
    }

    .stats-row {
        gap: 1.2rem;
    }

    .stat .number {
        font-size: 1.4rem;
    }

    .item-emoji {
        font-size: 2.2rem;
    }
}

@media (max-width: 480px) {
    .hero-section h1 {
        font-size: 1.5rem;
    }

    .stats-row {
        gap: 0.8rem;
    }

    .stat .number {
        font-size: 1.2rem;
    }

    .stat .label {
        font-size: 0.65rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════════╗
# ║  ESTADO DE SESSÃO                                           ║
# ╚══════════════════════════════════════════════════════════════╝

if "presenteando" not in st.session_state:
    st.session_state.presenteando = None

# Carregar dados atualizados
dados = carregar_dados()
config = dados["config"]
itens = dados["itens"]

NOME_CASAL = config["nome_casal"]

# Contadores
total = len(itens)
disponiveis = sum(1 for item in itens if item["status"] == "disponivel")
confirmados = sum(1 for item in itens if item["status"] == "confirmado")
pendentes = sum(1 for item in itens if item["status"] == "pendente")
presenteados = confirmados + pendentes


# ╔══════════════════════════════════════════════════════════════╗
# ║  HERO / CABEÇALHO                                           ║
# ╚══════════════════════════════════════════════════════════════╝

pct = int((presenteados / total * 100)) if total > 0 else 0

st.markdown(f"""
<div class="hero-section">
    <div class="icon">🏠</div>
    <h1>Casinha {NOME_CASAL}</h1>
    <p>Estamos montando nosso cantinho e você pode fazer parte dessa fase!
    Escolha um item da lista para nos presentear. 💛</p>
    <div class="hero-decor">✦ ✦ ✦</div>
</div>
""", unsafe_allow_html=True)

# Barra de progresso
st.markdown(f"""
<div class="progress-container">
    <div class="progress-bar-bg">
        <div class="progress-bar-fill" style="width: {pct}%;"></div>
    </div>
    <div class="progress-text">{presenteados} de {total} itens presenteados ({pct}%)</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="stats-row">
    <div class="stat">
        <div class="number">{total}</div>
        <div class="label">itens</div>
    </div>
    <div class="stat">
        <div class="number">{disponiveis}</div>
        <div class="label">disponíveis</div>
    </div>
    <div class="stat">
        <div class="number">{presenteados}</div>
        <div class="label">presenteados</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()


# ╔══════════════════════════════════════════════════════════════╗
# ║  PAINEL ADMIN (SIDEBAR)                                     ║
# ╚══════════════════════════════════════════════════════════════╝

with st.sidebar:
    st.markdown("## 🔑 Área dos Anfitriões")
    senha = st.text_input("Senha de acesso:", type="password", key="admin_senha")

    if senha == SENHA_ADMIN:
        st.success("Acesso liberado!")
        st.divider()

        # ── Abas do admin ──
        tab_resumo, tab_gerenciar, tab_adicionar, tab_config = st.tabs(
            ["📊 Resumo", "⚙️ Gerenciar", "➕ Adicionar", "🔧 Config"]
        )

        # ── Aba Resumo ──
        with tab_resumo:
            st.markdown("### Visão Geral")

            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("Disponíveis", disponiveis)
            with col_s2:
                st.metric("Pendentes", pendentes)
            with col_s3:
                st.metric("Confirmados", confirmados)

            valor_total = sum(item["preco"] for item in itens)
            valor_presenteado = sum(
                item["preco"] for item in itens if item["status"] in ("pendente", "confirmado")
            )
            st.markdown(f"**Valor total da lista:** R$ {valor_total:,.2f}")
            st.markdown(f"**Valor presenteado:** R$ {valor_presenteado:,.2f}")

            st.divider()

            # Pendentes de confirmação
            itens_pendentes = [item for item in itens if item["status"] == "pendente"]
            if itens_pendentes:
                st.markdown("### ⏳ Pendentes de Confirmação")
                for item_p in itens_pendentes:
                    st.markdown(f"- **{item_p['nome']}** — *{item_p['quem']}*")
                    if st.button(f"✅ Confirmar", key=f"admin_confirm_{item_p['id']}"):
                        for i, it in enumerate(dados["itens"]):
                            if it["id"] == item_p["id"]:
                                dados["itens"][i]["status"] = "confirmado"
                                break
                        salvar_dados(dados)
                        st.rerun()
            else:
                st.info("Nenhum presente pendente de confirmação.")

            # Lista completa
            st.divider()
            st.markdown("### 📋 Lista Completa")
            for item_l in itens:
                status_emoji = {"disponivel": "🟢", "pendente": "🟡", "confirmado": "💜"}.get(
                    item_l["status"], "⚪"
                )
                quem_txt = f" — {item_l['quem']}" if item_l["quem"] else ""
                st.markdown(
                    f"{status_emoji} **{item_l['nome']}** · R$ {item_l['preco']:.2f}{quem_txt}"
                )

        # ── Aba Gerenciar ──
        with tab_gerenciar:
            st.markdown("### Editar / Remover Itens")

            if not itens:
                st.info("Nenhum item na lista.")
            else:
                nomes_itens = [item["nome"] for item in itens]
                item_selecionado = st.selectbox(
                    "Selecione o item:", nomes_itens, key="admin_select_item"
                )

                # Encontrar item
                item_idx = next(
                    (i for i, it in enumerate(itens) if it["nome"] == item_selecionado), None
                )
                if item_idx is not None:
                    item_edit = itens[item_idx]

                    STATUS_LABELS = {
                        "disponivel": "🟢 Disponível",
                        "pendente": "🟡 Aguardando",
                        "confirmado": "💜 Confirmado",
                    }

                    with st.form(key="form_editar_item"):
                        st.markdown(f"#### ✏️ Editando: {item_edit['nome']}")

                        novo_nome = st.text_input("Nome:", value=item_edit["nome"])
                        novo_preco = st.number_input(
                            "Preço (R$):", value=float(item_edit["preco"]),
                            min_value=0.0, step=10.0, format="%.2f"
                        )
                        novo_emoji = st.text_input("Emoji:", value=item_edit["emoji"])
                        nova_desc = st.text_input("Descrição:", value=item_edit["desc"])

                        novo_status = st.radio(
                            "Status:",
                            list(STATUS_LABELS.keys()),
                            format_func=lambda x: STATUS_LABELS[x],
                            index=list(STATUS_LABELS.keys()).index(item_edit["status"]),
                        )
                        novo_quem = st.text_input("Quem presenteou:", value=item_edit.get("quem", ""))

                        # URL ou Foto
                        nova_url_foto = st.text_input(
                            "URL da imagem (Recomendado para nuvem):",
                            value=item_edit.get("foto", "") if str(item_edit.get("foto", "")).startswith("http") else ""
                        )
                        nova_foto = st.file_uploader(
                            "Ou faça upload de foto local:", type=["jpg", "jpeg", "png", "webp"],
                            key=f"foto_edit_{item_edit['id']}"
                        )

                        col_salvar, col_remover = st.columns(2)

                        with col_salvar:
                            salvar_btn = st.form_submit_button("💾 Salvar", use_container_width=True)

                        with col_remover:
                            remover_btn = st.form_submit_button("🗑️ Remover", use_container_width=True)

                        if salvar_btn:
                            dados["itens"][item_idx]["nome"] = novo_nome
                            dados["itens"][item_idx]["preco"] = novo_preco
                            dados["itens"][item_idx]["emoji"] = novo_emoji
                            dados["itens"][item_idx]["desc"] = nova_desc
                            dados["itens"][item_idx]["status"] = novo_status
                            dados["itens"][item_idx]["quem"] = novo_quem
                            dados["itens"][item_idx]["id"] = gerar_id(novo_nome)

                            # Definir foto baseado em URL ou Upload
                            if nova_url_foto.strip():
                                dados["itens"][item_idx]["foto"] = nova_url_foto.strip()
                            elif nova_foto:
                                # Otimizar e salvar foto no formato WebP
                                foto_nome = f"{gerar_id(novo_nome)}.webp"
                                foto_path = UPLOAD_DIR / foto_nome
                                foto_nome = otimizar_e_salvar_imagem(nova_foto, foto_path)
                                dados["itens"][item_idx]["foto"] = foto_nome
                            else:
                                # Se não mudou nem colou URL, mantém o valor antigo (se for local)
                                dados["itens"][item_idx]["foto"] = item_edit.get("foto", "")

                            salvar_dados(dados)
                            st.success(f"✅ '{novo_nome}' atualizado!")
                            st.rerun()

                        if remover_btn:
                            # Remover foto se existir
                            if item_edit.get("foto"):
                                foto_del = UPLOAD_DIR / item_edit["foto"]
                                if foto_del.exists():
                                    foto_del.unlink()
                            dados["itens"].pop(item_idx)
                            salvar_dados(dados)
                            st.success(f"🗑️ '{item_edit['nome']}' removido!")
                            st.rerun()

                    # Reordenar
                    st.divider()
                    st.markdown("#### ↕️ Reordenar")
                    col_up, col_down = st.columns(2)
                    with col_up:
                        if st.button("⬆️ Mover pra cima", key="move_up", use_container_width=True):
                            if item_idx > 0:
                                dados["itens"][item_idx], dados["itens"][item_idx - 1] = (
                                    dados["itens"][item_idx - 1], dados["itens"][item_idx]
                                )
                                salvar_dados(dados)
                                st.rerun()
                    with col_down:
                        if st.button("⬇️ Mover pra baixo", key="move_down", use_container_width=True):
                            if item_idx < len(dados["itens"]) - 1:
                                dados["itens"][item_idx], dados["itens"][item_idx + 1] = (
                                    dados["itens"][item_idx + 1], dados["itens"][item_idx]
                                )
                                salvar_dados(dados)
                                st.rerun()

        # ── Aba Adicionar ──
        with tab_adicionar:
            st.markdown("### Novo Item")

            with st.form(key="form_adicionar_item"):
                add_nome = st.text_input("Nome do item:")
                add_preco = st.number_input(
                    "Preço (R$):", min_value=0.0, step=10.0, format="%.2f"
                )
                add_emoji = st.text_input("Emoji:", value="🎁")
                add_desc = st.text_input("Descrição curta:")
                add_url_foto = st.text_input("URL da imagem (Recomendado para nuvem):", placeholder="Ex: https://imgur.com/...")
                add_foto = st.file_uploader(
                    "Ou faça upload de foto local:", type=["jpg", "jpeg", "png", "webp"],
                    key="foto_novo"
                )

                if st.form_submit_button("➕ Adicionar à lista", use_container_width=True):
                    if add_nome.strip():
                        novo_id = gerar_id(add_nome)

                        foto_nome = ""
                        if add_url_foto.strip():
                            foto_nome = add_url_foto.strip()
                        elif add_foto:
                            # Otimizar e salvar foto no formato WebP
                            foto_nome_arq = f"{novo_id}.webp"
                            foto_path = UPLOAD_DIR / foto_nome_arq
                            foto_nome = otimizar_e_salvar_imagem(add_foto, foto_path)

                        novo_item = {
                            "id": novo_id,
                            "nome": add_nome.strip(),
                            "preco": add_preco,
                            "emoji": add_emoji or "🎁",
                            "desc": add_desc.strip(),
                            "foto": foto_nome,
                            "status": "disponivel",
                            "quem": "",
                        }
                        dados["itens"].append(novo_item)
                        salvar_dados(dados)
                        st.success(f"✅ '{add_nome}' adicionado!")
                        st.rerun()
                    else:
                        st.warning("Preencha o nome do item.")

        # ── Aba Configurações ──
        with tab_config:
            st.markdown("### Configurações Gerais")

            with st.form(key="form_config"):
                cfg_nome = st.text_input("Nome do casal:", value=config["nome_casal"])
                cfg_chave = st.text_input("Chave PIX:", value=config["chave_pix"])
                cfg_tipo = st.selectbox(
                    "Tipo da chave:",
                    ["email", "cpf", "telefone", "aleatoria"],
                    index=["email", "cpf", "telefone", "aleatoria"].index(
                        config.get("tipo_chave", "email")
                    ),
                )
                cfg_beneficiario = st.text_input(
                    "Nome do beneficiário (PIX):",
                    value=config.get("nome_beneficiario", "SARA E LUIS"),
                )
                cfg_cidade = st.text_input(
                    "Cidade (PIX):",
                    value=config.get("cidade", "SAO PAULO"),
                )

                if st.form_submit_button("💾 Salvar Configurações", use_container_width=True):
                    dados["config"]["nome_casal"] = cfg_nome.strip()
                    dados["config"]["chave_pix"] = cfg_chave.strip()
                    dados["config"]["tipo_chave"] = cfg_tipo
                    dados["config"]["nome_beneficiario"] = cfg_beneficiario.strip()
                    dados["config"]["cidade"] = cfg_cidade.strip()
                    salvar_dados(dados)
                    st.success("✅ Configurações salvas!")
                    st.rerun()

            st.divider()
            st.markdown("### 📧 Email")
            try:
                email_ativo = st.secrets.get("email", {}).get("ativar", False)
                if email_ativo:
                    st.success("✅ Notificações por email ativas")
                else:
                    st.info("📧 Email desativado. Edite `.streamlit/secrets.toml` para ativar.")
            except Exception:
                st.info("📧 Email não configurado. Crie `.streamlit/secrets.toml`.")

    elif senha:
        st.error("Senha incorreta.")


# ╔══════════════════════════════════════════════════════════════╗
# ║  LISTA DE PRESENTES (VISÃO DO CONVIDADO)                    ║
# ╚══════════════════════════════════════════════════════════════╝

# Recarregar dados (pode ter mudado no admin)
dados = carregar_dados()
itens = dados["itens"]
config = dados["config"]

# Filtros e Busca
st.markdown("### 🔍 Encontre um Presente")
col_busca, col_filtro_status, col_filtro_preco = st.columns([2, 1, 1])

with col_busca:
    busca = st.text_input("Buscar por nome ou descrição:", placeholder="Ex: panela, cafeteira...", label_visibility="collapsed")

with col_filtro_status:
    filtro_status = st.selectbox(
        "Status:",
        ["Todos os status", "🟢 Disponíveis", "🟡 Aguardando", "💜 Reservados"],
        label_visibility="collapsed"
    )

with col_filtro_preco:
    filtro_preco = st.selectbox(
        "Faixa de preço:",
        ["Todos os valores", "Até R$ 100", "R$ 100 a R$ 250", "Acima de R$ 250"],
        label_visibility="collapsed"
    )

# Filtragem dos itens
itens_filtrados = itens

# 1. Filtro por Busca
if busca:
    itens_filtrados = [
        it for it in itens_filtrados 
        if busca.lower() in it["nome"].lower() or busca.lower() in it["desc"].lower()
    ]

# 2. Filtro por Status
if filtro_status == "🟢 Disponíveis":
    itens_filtrados = [it for it in itens_filtrados if it["status"] == "disponivel"]
elif filtro_status == "🟡 Aguardando":
    itens_filtrados = [it for it in itens_filtrados if it["status"] == "pendente"]
elif filtro_status == "💜 Reservados":
    itens_filtrados = [it for it in itens_filtrados if it["status"] == "confirmado"]

# 3. Filtro por Preço
if filtro_preco == "Até R$ 100":
    itens_filtrados = [it for it in itens_filtrados if it["preco"] <= 100.0]
elif filtro_preco == "R$ 100 a R$ 250":
    itens_filtrados = [it for it in itens_filtrados if 100.0 < it["preco"] <= 250.0]
elif filtro_preco == "Acima de R$ 250":
    itens_filtrados = [it for it in itens_filtrados if it["preco"] > 250.0]

st.write("")

if not itens_filtrados:
    st.info("Nenhum presente encontrado com os filtros selecionados.")
else:
    # Exibir itens em grid de 2 colunas
    colunas_por_linha = 2
    for i in range(0, len(itens_filtrados), colunas_por_linha):
        linha_itens = itens_filtrados[i:i + colunas_por_linha]
        cols = st.columns(colunas_por_linha)
        
        for col_idx, item in enumerate(linha_itens):
            with cols[col_idx]:
                with st.container(border=True):
                    # Card container
                    st.markdown('<div class="card-content">', unsafe_allow_html=True)
                    
                    # Foto ou Emoji
                    foto_exibida = False
                    foto_url_ou_path = item.get("foto", "")
                    
                    if foto_url_ou_path:
                        if str(foto_url_ou_path).startswith("http"):
                            st.image(foto_url_ou_path, use_container_width=True)
                            foto_exibida = True
                        else:
                            foto_path = UPLOAD_DIR / foto_url_ou_path
                            if foto_path.exists():
                                st.image(str(foto_path), use_container_width=True)
                                foto_exibida = True
                    
                    if not foto_exibida:
                        st.markdown(f'<div class="item-emoji">{item["emoji"]}</div>', unsafe_allow_html=True)
                    
                    # Informações do item
                    st.markdown(f'<div class="card-title">{item["nome"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="card-desc">{item["desc"]}</div>', unsafe_allow_html=True)
                    
                    # Footer do Card (Preço + Ação)
                    st.markdown('<div class="card-footer">', unsafe_allow_html=True)
                    st.markdown(f'<span class="preco">R$ {item["preco"]:.2f}</span>', unsafe_allow_html=True)
                    
                    status = item["status"]
                    if status == "disponivel":
                        if st.button("🎁 Presentear", key=f"gift_{item['id']}", use_container_width=True):
                            modal_presentear(item, config)
                    elif status == "pendente":
                        st.markdown('<span class="badge badge-pendente">⏳ Aguardando</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="badge badge-confirmado">💜 Reservado</span>', unsafe_allow_html=True)
                        
                    st.markdown('</div>', unsafe_allow_html=True) # Fim do card-footer
                    st.markdown('</div>', unsafe_allow_html=True) # Fim do card-content

# ╔══════════════════════════════════════════════════════════════╗
# ║  FOOTER                                                     ║
# ╚══════════════════════════════════════════════════════════════╝

st.markdown(
    f'<div class="footer">Feito com 💛 por {NOME_CASAL} · 🏠 Chá de Casa Nova</div>',
    unsafe_allow_html=True,
)
