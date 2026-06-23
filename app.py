import json
import io
import re
import base64
import os
import streamlit as st
import qrcode

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
        },
        "itens": []
    }

def carregar_dados() -> dict:
    # Se o arquivo físico existir no servidor, lê dele
    if os.path.exists(ARQUIVO_BANCO):
        try:
            with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
                dados = json.load(f)
                st.session_state["db_catalogo"] = dados
                return dados
        except Exception:
            pass
            
    # Se não existir ou falhar, usa o padrão/estado atual
    if "db_catalogo" not in st.session_state:
        st.session_state["db_catalogo"] = _catalogo_padrao()
        with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
            json.dump(st.session_state["db_catalogo"], f, ensure_ascii=False, indent=4)
            
    return st.session_state["db_catalogo"]

def salvar_dados(dados: dict) -> None:
    st.session_state["db_catalogo"] = dados
    # Grava diretamente no arquivo para persistir mesmo após refresh
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def gerar_id(nome: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", nome.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    import time
    return f"{slug}-{int(time.time())}"

# ╔══════════════════════════════════════════════════════════════╗
# ║  QR CODE PIX (CORRIGIDO)                                     ║
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

def gerar_payload_pix(
    chave: str, 
    nome_beneficiario: str, 
    cidade: str, 
    valor: float, 
    descricao: str
) -> str:
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

    # CORREÇÃO CRÍTICA AQUI: Removido o 'city=' incorreto que causava o TypeError
    payload_parts.extend([
        _tlv("58", "BR"),
        _tlv("59", nome_beneficiario[:25].upper()),
        _tlv("60", cidade[:15].upper()),
        _tlv("62", _tlv("05", "***")),
    ])
    payload_sem_crc = "".join(payload_parts) + "6304"
    return payload_sem_crc + _crc16_ccitt(payload_sem_crc)

def gerar_qrcode_pix(payload: str) -> bytes:
    qr = qrcode.QRCode(
        version=None, 
        error_correction=qrcode.constants.ERROR_CORRECT_M, 
        box_size=8, 
        border=2
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0B2545", back_color="#ffffff")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

dados = carregar_dados()
config = dados["config"]
st.set_page_config(
    page_title=f"Lista {config['nome_casal']}", 
    page_icon="🏠", 
    layout="centered"
)

# Injeção de CSS para garantir contraste e visibilidade
estilos_css = (
    "<style>"
    "h1, h2, h3, h4, h5, h6, p, label, .stMarkdown p { "
    "font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important; }"
    ".stApp { background-color: #F4F7FA !important; color: #2D3748 !important; }"
    "#MainMenu, footer, header { visibility: hidden; }"
    ".stExpander { border: 2px solid #0B2545 !important; "
    "border-radius: 12px !important; background-color: #ffffff !important; "
    "margin-top: 20px !important; }"
    ".stExpander summary p { color: #0B2545 !important; font-weight: 700 !important; }"
    "div[data-testid='stTabs'] button { color: #4A5568 !important; font-weight: 600 !important; }"
    "div[data-testid='stTabs'] button[aria-selected='true'] { "
    "color: #0B2545 !important; border-bottom: 3px solid #0B2545 !important; }"
    "div[data-testid='stVerticalBlockBorderWrapper'] { "
    "border-radius: 16px !important; border: 1px solid #E2E8F0 !important; "
    "background-color: #ffffff !important; padding: 24px !important; }"
    "div.stButton > button, div.stFormSubmitButton > button { "
    "background-color: #0B2545 !important; color: #ffffff !important; "
    "border-radius: 8px !important; font-weight: 600 !important; width: 100% !important; }"
    "label p { color: #0B2545 !important; font-weight: 600 !important; }"
    ".status-badge { padding: 6px 14px; border-radius: 30px; font-size: 0.75rem; "
    "font-weight: 700; text-transform: uppercase; display: inline-block; }"
    ".disponivel { background-color: #EBF8FF; color: #2B6CB0; }"
    ".pendente { background-color: #FEFCBF; color: #975A16; }"
    ".confirmado { background-color: #C6F6D5; color: #22543D; }"
    ".img-container img { border-radius: 12px !important; object-fit: cover !important; }"
    "div[role='dialog'] label p { color: #ffffff !important; font-size: 1.05rem !important; font-weight: 700 !important; }"
    "div[role='dialog'] input { color: #ffffff !important; background-color: #1E293B !important; border: 1px solid #475569 !important; }"
    "</style>"
)
st.markdown(estilos_css, unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════╗
# ║  MODAL DE PRESENTEAR                                         ║
# ╚══════════════════════════════════════════════════════════════╝

@st.dialog("🎁 Presentear")
def modal_presentear(item: dict, config: dict):
    t_nome = f"<h2 style='color:#F8FAFC; margin-bottom: 4px;'>{item['emoji']} {item['nome']}</h2>"
    st.markdown(t_nome, unsafe_allow_html=True)
    
    t_preco = f"<p style='font-size: 1.2rem; color: #CBD5E1;'>Valor do Presente: <strong style='color:#38BDF8; font-size: 1.4rem;'>R$ {item['preco']:.2f}</strong></p>"
    st.markdown(t_preco, unsafe_allow_html=True)
    
    payload = gerar_payload_pix(
        chave=config["chave_pix"],
        nome_beneficiario=config["nome_beneficiario"],
        cidade=config["cidade"],
        valor=item["preco"],
        descricao=item["id"][:25]
    )
    
    html_instrucoes = (
        "<div style='background-color:#0F172A; padding:16px; border-radius:8px; border: 1px solid #334155; margin-bottom: 20px;'>"
        "<span style='color:#38BDF8; font-weight:bold; font-size:1.05rem; display:block; margin-bottom:6px;'>Passo a passo para pagar:</span>"
        "<p style='color:#E2E8F0; margin:4px 0; font-size:0.95rem;'>1. Abra o aplicativo do seu banco de preferência.</p>"
        "<p style='color:#E2E8F0; margin:4px 0; font-size:0.95rem;'>2. Vá na área Pix e escolha <strong>Ler QR Code</strong> ou <strong>Pix Copia e Cola</strong>.</p>"
        "</div>"
    )
    st.markdown(html_instrucoes, unsafe_allow_html=True)
    
    colunas = st.columns([1, 1.3])
    
    with colunas[0]:
        st.image(gerar_qrcode_pix(payload), width=150)
    with colunas[1]:
        st.markdown("<p style='color:#F8FAFC; font-weight:bold; margin-bottom:4px;'>Código Pix Copia e Cola:</p>", unsafe_allow_html=True)
        st.code(payload, language="text")
        
    st.markdown("<hr style='border:0; border-top:1px solid #334155; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#F8FAFC; font-size: 1.2rem; margin-bottom:10px;'>Avise os Noivos</h3>", unsafe_allow_html=True)
    
    with st.form(key=f"form_{item['id']}"):
        nome_convidado = st.text_input("Seu nome completo:", placeholder="Digite seu nome aqui...")
        
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.form_submit_button("✓ Confirme que fez o Pix"):
            quem = nome_convidado.strip() or "Anônimo"
            dados_atuais = carregar_dados()
            for i, it in enumerate(dados_atuais["itens"]):
                if it["id"] == item["id"]:
                    dados_atuais["itens"][i]["status"] = "pendente"
                    dados_atuais["itens"][i]["quem"] = quem
                    break
            salvar_dados(dados_atuais)
            st.success("Obrigado! Seu presente foi avisado aos noivos. 🤍")
            st.rerun()

# ╔══════════════════════════════════════════════════════════════╗
# ║  VISÃO PÚBLICA                                               ║
# ╚══════════════════════════════════════════════════════════════╝

cabecalho = (
    "<div style='text-align: center; padding: 20px;'>"
    f"<h1 style='color: #0B2545;'>Casinha {config['nome_casal']}</h1>"
    "<p>Escolha um dos itens para o nosso novo lar! 🏠🤍</p>"
    "</div>"
)
st.markdown(cabecalho, unsafe_allow_html=True)

itens = dados["itens"]

if not itens:
    vazio = (
        "<div style='text-align:center; padding: 30px; border: 1px dashed #0B2545; border-radius: 8px;'>"
        "A lista está vazia no momento. Use o painel de controle abaixo para adicionar os presentes!"
        "</div>"
    )
    st.markdown(vazio, unsafe_allow_html=True)
else:
    for item in itens:
        with st.container(border=True):
            cols_item = st.columns([1.1, 2, 1])
            
            with cols_item[0]:
                if item.get("foto"):
                    img_html = f"<div class='img-container'><img src='data:image/jpeg;base64,{item['foto']}' width='100%'/></div>"
                    st.markdown(img_html, unsafe_allow_html=True)
                else:
                    st.markdown("<div style='font-size:2rem;text-align:center;'>🎁</div>", unsafe_allow_html=True)
                    
            with cols_item[1]:
                st.markdown(f"<h3>{item['emoji']} {item['nome']}</h3>", unsafe_allow_html=True)
                st.markdown(f"<span style='font-weight:bold;'>R$ {item['preco']:.2f}</span>", unsafe_allow_html=True)
                
                if item["status"] == "disponivel":
                    st.markdown("<br><span class='status-badge disponivel'>Disponível</span>", unsafe_allow_html=True)
                elif item["status"] == "pendente":
                    st.markdown(f"<br><span class='status-badge pendente'>Pendente ({item['quem']})</span>", unsafe_allow_html=True)
                elif item["status"] == "confirmado":
                    st.markdown(f"<br><span class='status-badge confirmado'>De: {item['quem']} 🤍</span>", unsafe_allow_html=True)
            
            with cols_item[2]:
                if item["status"] == "disponivel":
                    if st.button("Presentear", key=f"btn_{item['id']}", use_container_width=True):
                        modal_presentear(item, config)

# ╔══════════════════════════════════════════════════════════════╗
# ║  PAINEL DE CONTROLE                                          ║
# ╚══════════════════════════════════════════════════════════════╝

st.markdown("<br>", unsafe_allow_html=True)
admin_panel = st.expander("🔑 Painel do Casal", expanded=False)

with admin_panel:
    with st.form(key="form_admin"):
        senha = st.text_input("Senha:", type="password")
        entrar = st.form_submit_button("Acessar")
    
    if senha == SENHA_ADMIN:
        tab1, tab2, tab3 = st.tabs(["Gerenciar", "Adicionar", "Configuração"])
        
        with tab1:
            if not itens:
                st.info("Nenhum item.")
            else:
                for idx, item in enumerate(itens):
                    c_admin = st.columns([2, 1, 2])
                    
                    with c_admin[0]:
                        st.write(f"{item['nome']} (R$ {item['preco']:.2f})")
                    
                    with c_admin[1]:
                        if item["status"] == "pendente":
                            if st.button("✅ Conf.", key=f"c_{item['id']}"):
                                dados["itens"][idx]["status"] = "confirmado"
                                salvar_dados(dados)
                                st.rerun()
                        if st.button("❌ Rem.", key=f"d_{item['id']}"):
                            dados["itens"].pop(idx)
                            salvar_dados(dados)
                            st.rerun()
                            
                    with c_admin[2]:
                        opcoes = ["disponivel", "pendente", "confirmado"]
                        i_padrao = opcoes.index(item["status"]) if item["status"] in opcoes else 0
                        novo = st.selectbox("Status:", opcoes, index=i_padrao, key=f"s_{item['id']}")
                        
                        if novo != item["status"]:
                            dados["itens"][idx]["status"] = novo
                            if novo == "disponivel":
                                dados["itens"][idx]["quem"] = ""
                            salvar_dados(dados)
                            st.rerun()

        with tab2:
            with st.form(key="form_add", clear_on_submit=True):
                n_nome = st.text_input("Nome:")
                n_preco = st.number_input("Preço:", min_value=1.0, value=150.0)
                n_emoji = st.text_input("Emoji:", value="🎁")
                n_desc = st.text_input("Descrição:")
                foto = st.file_uploader("Foto:", type=["jpg", "png"])
                
                if st.form_submit_button("Salvar Item"):
                    if n_nome.strip():
                        b64 = ""
                        if foto:
                            b64 = base64.b64encode(foto.read()).decode("utf-8")
                            
                        dados["itens"].append({
                            "id": gerar_id(n_nome),
                            "nome": n_nome.strip(),
                            "preco": float(n_preco),
                            "emoji": n_emoji.strip() or "🎁",
                            "desc": n_desc.strip(),
                            "status": "disponivel",
                            "quem": "",
                            "foto": b64
                        })
                        salvar_dados(dados)
                        st.success("Adicionado!")
                        st.rerun()

        with tab3:
            with st.form(key="form_cfg"):
                c_casal = st.text_input("Casal:", value=config["nome_casal"])
                c_chave = st.text_input("Chave Pix:", value=config["chave_pix"])
                c_nome = st.text_input("Beneficiário:", value=config["nome_beneficiario"])
                c_cidade = st.text_input("Cidade:", value=config["cidade"])
                
                if st.form_submit_button("Salvar Config."):
                    dados["config"]["nome_casal"] = c_casal
                    dados["config"]["chave_pix"] = c_chave.strip()
                    dados["config"]["nome_beneficiario"] = c_nome.strip().upper()
                    dados["config"]["cidade"] = c_cidade.strip().upper()
                    salvar_dados(dados)
                    st.success("Salvo!")
                    st.rerun()
