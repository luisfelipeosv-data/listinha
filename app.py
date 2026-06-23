"""
Casinha Sara & Luis — Lista de Presentes Premium 🏠
Design Corrigido: Helvetica Autêntica, Azul Noturno e Proteção de Layout
"""

import json
import io
import re
import base64
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

DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
_file_lock = threading.Lock()

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
# ║  CONFIGURAÇÃO DA PÁGINA                                      ║
# ╚══════════════════════════════════════════════════════════════╝

dados = carregar_dados()
config = dados["config"]
st.set_page_config(page_title=f"Lista {config['nome_casal']}", page_icon="🏠", layout="centered")

# ╔══════════════════════════════════════════════════════════════╗
# ║  ARQUITETURA DE DESIGN CSS (PROTEÇÃO CONTRA QUEBRAS)         ║
# ╚══════════════════════════════════════════════════════════════╝

st.markdown("""
<style>
/* Aplicação segura da fonte Helvetica sem destruir os ícones nativos */
html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, span, label, li, input, button, select {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
}

/* Fundo Premium Off-White Luxury */
.stApp { 
    background: linear-gradient(135deg, #F4F7FA 0%, #E9EFF5 100%) !important; 
    color: #2D3748 !important; 
}
#MainMenu, footer, header { visibility: hidden; }

/* Proteção e Estilização Forçada do Modal (Resolve contraste em modo escuro) */
div[role="dialog"] {
    background-color: #ffffff !important;
    color: #2D3748 !important;
    border-radius: 16px !important;
    border: 1px solid #E2E8F0 !important;
}
div[role="dialog"] h3, div[role="dialog"] span, div[role="dialog"] p, div[role="dialog"] div {
    color: #2D3748 !important;
}

/* Estilização dos Cards de Presentes */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 10px 25px rgba(11, 37, 69, 0.04) !important;
    background-color: #ffffff !important;
    padding: 24px !important;
    margin-bottom: 15px !important;
}

/* Botões do Sistema — Azul Escuro Premium */
div.stButton > button, div.stFormSubmitButton > button {
    background-color: #0B2545 !important;
    color: #ffffff !important;
    border: 1px solid #0B2545 !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease-in-out !important;
    width: 100% !important;
    box-shadow: 0 4px 6px rgba(11, 37, 69, 0.1) !important;
}

div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    background-color: #134074 !important;
    border-color: #134074 !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 12px rgba(11, 37, 69, 0.15) !important;
}

/* Badges de Status Modernas */
.status-badge {
    padding: 6px 14px;
    border-radius: 30px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    display: inline-block;
    margin-top: 8px;
    letter-spacing: 0.5px;
}
.disponivel { background-color: #EBF8FF; color: #2B6CB0; border: 1px solid #BEE3F8; }
.pendente { background-color: #FEFCBF; color: #975A16; border: 1px solid #FEF08A; }
.confirmado { background-color: #C6F6D5; color: #22543D; border: 1px solid #9AE6B4; }

.img-container img {
    border-radius: 12px !important;
    object-fit: cover !important;
}
</style>
""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════╗
# ║  MODAL DE PAGAMENTO (ALINHADO COM O DESIGN)                  ║
# ╚══════════════════════════════════════════════════════════════╝

@st.dialog("🎁 Presentear")
def modal_presentear(item: dict, config: dict):
    # Forçar cores internas do modal via HTML inline seguro para evitar conflitos do Streamlit
    st.markdown(f"<h2 style='color:#0B2545; font-weight:700; margin-top:0;'>{item['emoji']} {item['nome']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:1.1rem; color:#4A5568;'>Valor sugerido: <strong style='color:#0B2545; font-size:1.3rem;'>R$ {item['preco']:.2f}</strong></p>", unsafe_allow_html=True)
    
    payload = gerar_payload_pix(
        chave=config["chave_pix"],
        nome_beneficiario=config["nome_beneficiario"],
        cidade=config["cidade"],
        valor=item["preco"],
        descricao=item["id"][:25]
    )
    
    st.markdown("""
    <div style='background-color:#F7FAFC; padding:15px; border-radius:10px; font-size:0.9rem; margin-bottom:20px; border-left:4px solid #0B2545; color:#4A5568;'>
        <strong style='color:#0B2545;'>Como realizar o pagamento:</strong><br>
        1. Acesse o app do seu banco de preferência.<br>
        2. Escolha pagar via Pix e escaneie o QR Code ou utilize o Copia e Cola.
    </div>
    """, unsafe_allow_html=True)
    
    col_qr, col_copy = st.columns([1, 1.2])
    with col_qr:
        st.image(gerar_qrcode_pix(payload), width=160)
    with col_copy:
        st.markdown("<p style='font-weight:600; margin-bottom:5px; color:#0B2545;'>Pix Copia e Cola:</p>", unsafe_allow_html=True)
        st.code(payload, language="text")
        
    st.divider()
    st.markdown("<h3 style='color:#0B2545; font-size:1.2rem; font-weight:700;'>Confirme seu Presente</h3>", unsafe_allow_html=True)
    
    with st.form(key=f"form_modal_{item['id']}"):
        nome_convidado = st.text_input("Seu nome completo:", placeholder="Ex: Ana Silva")
        if st.form_submit_button("Já fiz o Pix! Confirmar"):
            quem = nome_convidado.strip() or "Anônimo"
            dados_atuais = carregar_dados()
            for i, it in enumerate(dados_atuais["itens"]):
                if it["id"] == item["id"]:
                    dados_atuais["itens"][i]["status"] = "pendente"
                    dados_atuais["itens"][i]["quem"] = quem
                    break
            salvar_dados(dados_atuais)
            st.success("Obrigado! Seu presente foi registrado e aguarda confirmação dos noivos. 🤍")
            st.rerun()

# ╔══════════════════════════════════════════════════════════════╗
# ║  VISÃO PÚBLICA (CABEÇALHO E ITENS)                           ║
# ╚══════════════════════════════════════════════════════════════╝

st.markdown(f"""
<div style='text-align: center; padding: 45px 10px 25px 10px;'>
    <h1 style='color: #0B2545; font-weight: 800; font-size: 2.8rem; margin-bottom: 8px; letter-spacing: -0.5px;'>Casinha {config['nome_casal']}</h1>
    <p style='color: #4A5568; font-size: 1.15rem; max-width: 540px; margin: 0 auto; line-height: 1.6;'>
        Bem-vindo à nossa lista de presentes. Escolha um dos itens abaixo para nos ajudar a construir nosso novo lar! 🏠🤍
    </p>
</div>
""", unsafe_allow_html=True)

itens = dados["itens"]

if not itens:
    st.markdown("""
    <div style='text-align:center; padding: 50px; background: white; border-radius:16px; border: 1px dashed #CBD5E0; margin-top: 20px;'>
        <span style='font-size: 2.2rem;'>✨</span>
        <p style='color: #718096; margin-top: 12px; font-weight: 500; font-size:1.05rem;'>A lista está sendo preparada. Use o painel abaixo para cadastrar itens!</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for item in itens:
        with st.container(border=True):
            col_img, col_info, col_btn = st.columns([1.1, 2, 1])
            
            with col_img:
                if item.get("foto"):
                    st.markdown('<div class="img-container">', unsafe_allow_html=True)
                    st.image(f"data:image/jpeg;base64,{item['foto']}", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style='height: 110px; background-color: #EDF2F7; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #A0AEC0; font-size: 2rem;'>
                        🎁
                    </div>
                    """, unsafe_allow_html=True)
                    
            with col_info:
                st.markdown(f"<h3 style='color: #0B2545; font-size: 1.3rem; margin: 0 0 4px 0; font-weight:700;'>{item['emoji']} {item['nome']}</h3>", unsafe_allow_html=True)
                if item["desc"]:
                    st.markdown(f"<p style='color: #718096; font-size: 0.9rem; margin: 0 0 8px 0; font-style: italic;'>{item['desc']}</p>", unsafe_allow_html=True)
                st.markdown(f"<span style='font-size: 1.35rem; font-weight: 800; color: #0B2545;'>R$ {item['preco']:.2f}</span>", unsafe_allow_html=True)
                
                if item["status"] == "disponivel":
                    st.markdown("<br><span class='status-badge disponivel'>Disponível</span>", unsafe_allow_html=True)
                elif item["status"] == "pendente":
                    st.markdown(f"<br><span class='status-badge pendente'>Aguardando Validação ({item['quem']})</span>", unsafe_allow_html=True)
                elif item["status"] == "confirmado":
                    st.markdown(f"<br><span class='status-badge confirmado'>Presenteado por {item['quem']} 🤍</span>", unsafe_allow_html=True)
            
            with col_btn:
                st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
                if item["status"] == "disponivel":
                    if st.button("Presentear", key=f"btn_{item['id']}", use_container_width=True):
                        modal_presentear(item, config)

# ╔══════════════════════════════════════════════════════════════╗
# ║  PAINEL DE CONTROLE EXCLUSIVO                                ║
# ╚══════════════════════════════════════════════════════════════╝

st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
expander_admin = st.expander("🔑 Painel de Controle Exclusivo do Casal", expanded=False)

with expander_admin:
    senha_digitada = st.text_input("Senha de Acesso:", type="password", placeholder="Digite a senha administrativa")
    
    if senha_digitada == SENHA_ADMIN:
        st.success("Autenticação realizada com sucesso!")
        tab_listar, tab_add, tab_cfg = st.tabs(["⚙️ Gerenciar Itens", "➕ Adicionar com Foto", "🔧 Configurações da Conta"])
        
        with tab_listar:
            if not itens:
                st.info("Nenhum item cadastrado.")
            else:
                for idx, item in enumerate(itens):
                    col_id, col_edit, col_status = st.columns([2.5, 1.5, 2])
                    
                    with col_id:
                        st.markdown(f"**{item['emoji']} {item['nome']}**<br><span style='color:#0B2545;font-weight:600;'>R$ {item['preco']:.2f}</span>", unsafe_allow_html=True)
                    
                    with col_edit:
                        if item["status"] == "pendente":
                            if st.button("✅ Confirmar", key=f"conf_{item['id']}", use_container_width=True):
                                dados["itens"][idx]["status"] = "confirmado"
                                salvar_dados(dados)
                                st.rerun()
                        
                        if st.button("❌ Remover", key=f"del_{item['id']}", use_container_width=True):
                            dados["itens"].pop(idx)
                            salvar_dados(dados)
                            st.rerun()
                            
                    with col_status:
                        status_options = ["disponivel", "pendente", "confirmado"]
                        default_idx = status_options.index(item["status"]) if item["status"] in status_options else 0
                        
                        novo_status = st.selectbox(
                            "Status manual:", 
                            status_options, 
                            index=default_idx,
                            key=f"sel_{item['id']}"
                        )
                        if novo_status != item["status"]:
                            dados["itens"][idx]["status"] = novo_status
                            if novo_status == "disponivel":
                                dados["itens"][idx]["quem"] = ""
                            salvar_dados(dados)
                            st.rerun()

        with tab_add:
            with st.form(key="form_adicionar_item", clear_on_submit=True):
                st.subheader("Novo Presente")
                novo_nome = st.text_input("Nome do Item:", placeholder="Ex: Cafeteira Expresso")
                novo_preco = st.number_input("Preço Sugerido (R$):", min_value=1.0, value=150.0, step=10.0)
                
                col_inputs = st.columns([1, 3])
                with col_inputs[0]:
                    novo_emoji = st.text_input("Emoji:", value="🎁", max_chars=2)
                with col_inputs[1]:
                    nova_desc = st.text_input("Mensagem/Descrição:", placeholder="Ex: Para nossas manhãs perfeitas")
                
                foto_upload = st.file_uploader("Selecione uma imagem do produto (Opcional):", type=["jpg", "jpeg", "png"])
                
                if st.form_submit_button("Salvar Presente na Lista"):
                    if novo_nome.strip():
                        foto_b64 = ""
                        if foto_upload is not None:
                            bytes_data = foto_upload.read()
                            foto_b64 = base64.b64encode(bytes_data).decode("utf-8")
                            
                        novo_item = {
                            "id": gerar_id(novo_nome),
                            "nome": novo_nome.strip(),
                            "preco": float(novo_preco),
                            "emoji": novo_emoji.strip() or "🎁",
                            "desc": nova_desc.strip(),
                            "status": "disponivel",
                            "quem": "",
                            "foto": foto_b64
                        }
                        dados["itens"].append(novo_item)
                        salvar_dados(dados)
                        st.success(f"'{novo_nome}' adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Por favor, preencha o nome do item.")

        with tab_cfg:
            st.subheader("Configurações do Sistema Pix")
            cfg_casal = st.text_input("Nome do Casal na Tela:", value=config["nome_casal"])
            cfg_chave = st.text_input("Sua Chave Pix Definitiva:", value=config["chave_pix"])
            cfg_titular = st.text_input("Nome do Titular da Conta (Sem acentos):", value=config["nome_beneficiario"])
            cfg_cidade = st.text_input("Cidade da Conta (Sem acentos):", value=config["cidade"])
            
            if st.button("Salvar Todas as Configurações"):
                dados["config"]["nome_casal"] = cfg_casal
                dados["config"]["chave_pix"] = cfg_chave.strip()
                dados["config"]["nome_beneficiario"] = cfg_titular.strip().upper()
                dados["config"]["cidade"] = cfg_cidade.strip().upper()
                salvar_dados(dados)
                st.success("Configurações salvas com sucesso!")
                st.rerun()
