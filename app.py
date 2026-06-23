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
            quem = nome_convidado.strip() or "Anônimo"
            dados_atuais = carregar_dados()
            for i, it in enumerate(dados_atuais["itens"]):
                if it["id"] == item["id"]:
                    dados_atuais["itens"][i]["status"] = "pendente"
                    dados_atuais["itens"][i]["quem"] = quem
                    break
            salvar_dados(dados_atuais)
            st.success("Obrigado! Avisamos os noivos para confirmar o recebimento. 🤍")
            st.rerun()

# ╔══════════════════════════════════════════════════════════════╗
# ║  CONFIGURAÇÃO E ESTILO (HELVETICA / AZUL E BRANCO)           ║
# ╚══════════════════════════════════════════════════════════════╝

dados = carregar_dados()
config = dados["config"]
st.set_page_config(page_title=f"Lista {config['nome_casal']}", page_icon="🏠", layout="centered")

st.markdown("""
<style>
* { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important; }
.stApp { background-color: #ffffff; color: #333333; }
#MainMenu, footer, header { visibility: hidden; }

/* Cards minimalistas */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
    border: 1px solid #e1e8ed !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
    background: #ffffff !important;
}

/* Botões Customizados em Azul Escuro */
.stButton > button {
    border-radius: 8px !important;
    background-color: #0B2545 !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 500 !important;
}
.stButton > button:hover {
    background-color: #134074 !important;
}

/* Badges de Status */
.status-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
    margin-top: 5px;
}
.disponivel { background-color: #e3effd; color: #134074; }
.pendente { background-color: #fff3cd; color: #856404; }
.confirmado { background-color: #d4edda; color: #155724; }
</style>
""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════╗
# ║  VISÃO PÚBLICA (CABEÇALHO E ITENS)                           ║
# ╚══════════════════════════════════════════════════════════════╝

st.markdown(f"""
<div style='text-align: center; padding: 30px 10px;'>
    <h1 style='color: #0B2545; font-weight: 700; font-size: 2.5rem; margin-bottom: 5px;'>Casinha {config['nome_casal']}</h1>
    <p style='color: #666; font-size: 1.1rem; max-width: 500px; margin: 0 auto;'>
        Estamos montando nosso cantinho. Escolha um item abaixo para nos presentear de forma simples e segura! 🤍
    </p>
</div>
""", unsafe_allow_html=True)

itens = dados["itens"]

if not itens:
    st.info("A lista está sendo preparada pelos noivos. Volte em breve! ✨")
else:
    for item in itens:
        with st.container(border=True):
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.markdown(f"### {item['emoji']} {item['nome']}")
                st.markdown(f"*{item['desc']}*")
                st.markdown(f"<span style='font-size:1.2rem; font-weight:700; color:#0B2545;'>R$ {item['preco']:.2f}</span>", unsafe_allow_html=True)
                
                if item["status"] == "disponivel":
                    st.markdown("<span class='status-badge disponivel'>Disponível</span>", unsafe_allow_html=True)
                elif item["status"] == "pendente":
                    st.markdown(f"<span class='status-badge pendente'>Aguardando validação ({item['quem']})</span>", unsafe_allow_html=True)
                elif item["status"] == "confirmado":
                    st.markdown(f"<span class='status-badge confirmado'>Presenteado por {item['quem']} 🤍</span>", unsafe_allow_html=True)
            
            with col_btn:
                st.write("") 
                if item["status"] == "disponivel":
                    if st.button("Presentear", key=f"btn_{item['id']}", use_container_width=True):
                        modal_presentear(item, config)

# ╔══════════════════════════════════════════════════════════════╗
# ║  PAINEL DE CONTROLE                                          ║
# ╚══════════════════════════════════════════════════════════════╝

st.divider()
expander_admin = st.expander("🔑 Painel de Controle do Casal", expanded=False)

with expander_admin:
    senha_digitada = st.text_input("Digite a senha do casal:", type="password")
    
    if senha_digitada == SENHA_ADMIN:
        st.success("Acesso Liberado!")
        tab_listar, tab_add, tab_cfg = st.tabs(["⚙️ Gerenciar Itens", "➕ Adicionar Novo", "🔧 Configurações Gerais"])
        
        with tab_listar:
            if not itens:
                st.info("Nenhum item adicionado ainda.")
            else:
                for idx, item in enumerate(itens):
                    col_id, col_edit, col_status = st.columns([2, 2, 2])
                    
                    with col_id:
                        st.markdown(f"**{item['nome']}**<br>R$ {item['preco']:.2f}", unsafe_allow_html=True)
                    
                    with col_edit:
                        if item["status"] == "pendente":
                            if st.button("✅ Confirmar Pix", key=f"conf_{item['id']}"):
                                dados["itens"][idx]["status"] = "confirmado"
                                salvar_dados(dados)
                                st.rerun()
                        
                        if st.button("❌ Remover Item", key=f"del_{item['id']}"):
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
                st.subheader("Cadastrar Novo Presente")
                novo_nome = st.text_input("Nome do Item:", placeholder="Ex: Jogo de Panelas")
                novo_preco = st.number_input("Preço Sugerido (R$):", min_value=1.0, value=50.0, step=5.0)
                novo_emoji = st.text_input("Emoji representativo:", value="🎁", max_chars=2)
                nova_desc = st.text_input("Breve descrição/recado:", placeholder="Ex: Para nossos jantares especiais")
                
                if st.form_submit_button("Salvar na Lista", use_container_width=True):
                    if novo_nome.strip():
                        novo_item = {
                            "id": gerar_id(novo_nome),
                            "nome": novo_nome.strip(),
                            "preco": float(novo_preco),
                            "emoji": novo_emoji.strip() or "🎁",
                            "desc": nova_desc.strip(),
                            "status": "disponivel",
                            "quem": ""
                        }
                        dados["itens"].append(novo_item)
                        salvar_dados(dados)
                        st.success(f"'{novo_nome}' adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error("O nome do item é obrigatório.")

        with tab_cfg:
            st.subheader("Ajustar Dados da Conta")
            cfg_casal = st.text_input("Nome do Casal:", value=config["nome_casal"])
            cfg_chave = st.text_input("Sua Chave Pix:", value=config["chave_pix"])
            cfg_titular = st.text_input("Nome do Titular (Igual no banco):", value=config["nome_beneficiario"])
            cfg_cidade = st.text_input("Cidade (Sem acentos):", value=config["cidade"])
            
            if st.button("Salvar Configurações", use_container_width=True):
                dados["config"]["nome_casal"] = cfg_casal
                dados["config"]["chave_pix"] = cfg_chave.strip()
                dados["config"]["nome_beneficiario"] = cfg_titular.strip().upper()
                dados["config"]["cidade"] = cfg_cidade.strip().upper()
                salvar_dados(dados)
                st.success("Configurações salvas e atualizadas!")
                st.rerun()
