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
# ║  INTEGRAÇÃO MERCADO PAGO                                     ║
# ╚══════════════════════════════════════════════════════════════╝

def gerar_link_cartao_mercado_pago(item: dict, access_token: str) -> str:
    if not access_token or access_token.strip() == "":
        return None
        
    token_limpo = access_token.strip()
    url = "https://api.mercadopago.com/checkout/preferences"
    
    headers = {
        "Authorization": f"Bearer {token_limpo}",
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
        "back_urls": {
            "success": "https://lista-sls.streamlit.app",
            "failure": "https://lista-sls.streamlit.app",
            "pending": "https://lista-sls.streamlit.app"
        },
        "auto_return": "approved"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            return response.json().get("init_point")
    except Exception:
        pass
        
    return None

# ╔══════════════════════════════════════════════════════════════╗
# ║  QR CODE PIX NATIVO                                          ║
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

def gerar_payload_pix(chave: str, nome_beneficiario: str, city: str, valor: float, descricao: str) -> str:
    chave_limpa = remover_acentos(chave)
    nome_limpo = remover_acentos(nome_beneficiario[:25]).upper()
    cidade_limpa = remover_acentos(city[:15]).upper()
    desc_limpa = remover_acentos(descricao[:25])

    gui = _tlv("00", "BR.GOV.BCB.PIX")
    chave_field = _tlv("01", chave_limpa)
    desc_field = _tlv("02", desc_limpa)
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
        _tlv("59", nome_limpo),
        _tlv("60", cidade_limpa), 
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

# Injeção de CSS
estilos_css = (
    "<style>"
    "h1, h2, h3, h4, h5, h6, p, label, .stMarkdown p { "
    "font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important; }"
    ".stApp { background-color: #F4F7FA !important; color: #2D3748 !important; }"
    "#MainMenu, footer, header { visibility: hidden; }"
    
    ".stExpander { border: 2px solid #0B2545 !important; "
    "border-radius: 12px !important; background-color: #ffffff !important; "
    "margin-top: 40px !important; }"
    ".stExpander summary p { color: #0B2545 !important; font-weight: 700 !important; }"
    "div[data-testid='stTabs'] button { color: #4A5568 !important; font-weight: 600 !important; }"
    "div[data-testid='stTabs'] button[aria-selected='true'] { "
    "color: #0B2545 !important; border-bottom: 3px solid #0B2545 !important; }"
    
    "div[data-testid='stVerticalBlock']:has(> div.element-container div.anuncio-identificador) { "
    "background-color: #ffffff !important; "
    "border: 2px solid #0B2545 !important; "
    "border-radius: 16px !important; "
    "padding: 22px !important; "
    "margin-bottom: 25px !important; "
    "box-shadow: 0 10px 15px -3px rgba(11, 37, 69, 0.06) !important; }"
    
    "div.stButton > button, div.stFormSubmitButton > button { "
    "background-color: #0B2545 !important; color: #ffffff !important; "
    "border-radius: 8px !important; font-weight: 600 !important; width: 100% !important; }"
    "label p { color: #0B2545 !important; font-weight: 600 !important; }"
    
    ".status-badge { padding: 6px 16px; border-radius: 30px; font-size: 0.85rem; "
    "font-weight: 700; display: inline-block; text-align: center; }"
    ".disponivel { background-color: #EBF8FF !important; color: #2B6CB0 !important; border: 1px solid #BEE3F8 !important; }"
    ".confirmado { background-color: #F0FDF4 !important; color: #166534 !important; border: 1px solid #BBF7D0 !important; }"
    
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
    st.markdown(f"<h2 style='color:#F8FAFC; margin-bottom: 4px;'>{item['emoji']} {item['nome']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 1.2rem; color: #CBD5E1;'>Valor: <strong style='color:#38BDF8; font-size: 1.4rem;'>R$ {item['preco']:.2f}</strong></p>", unsafe_allow_html=True)
    
    payload_pix = gerar_payload_pix(
        chave=config["chave_pix"], nome_beneficiario=config["nome_beneficiario"],
        city=config["cidade"], valor=item["preco"], descricao=item["id"][:25]
    )
    link_cartao = gerar_link_cartao_mercado_pago(item, config.get("mp_access_token", ""))
    
    if link_cartao:
        opcao_pgto = st.radio("Escolha a forma de pagamento:", ["Pix (Imediato)", "Cartão de Crédito (Até 12x)"], horizontal=True)
    else:
        opcao_pgto = "Pix (Imediato)"
        
    st.markdown("<hr style='border:0; border-top:1px solid #334155; margin: 15px 0;'>", unsafe_allow_html=True)
    
    if opcao_pgto == "Pix (Imediato)":
        html_instrucoes = (
            "<div style='background-color:#0F172A; padding:12px; border-radius:8px; border: 1px solid #334155; margin-bottom: 15px;'>",
            "<p style='color:#E2E8F0; margin:0; font-size:0.95rem;'>Abra o app do seu banco e pague usando o QR Code ou Copia e Cola abaixo:</p>",
            "</div>"
        )
        st.markdown("".join(html_instrucoes), unsafe_allow_html=True)
        col_qr = st.columns([1, 1.3])
        with col_qr[0]:
            st.image(gerar_qrcode_pix(payload_pix), width=140)
        with col_qr[1]:
            st.markdown("<p style='color:#F8FAFC; font-size:0.9rem; font-weight:bold; margin:0;'>Código Copia e Cola:</p>", unsafe_allow_html=True)
            st.code(payload_pix, language="text")
    else:
        st.markdown("<p style='color:#E2E8F0; font-size:0.95rem;'>Clique no botão abaixo para realizar o pagamento parcelado com total segurança no Mercado Pago:</p>", unsafe_allow_html=True)
        st.link_button("💳 Ir para Pagamento em Cartão", link_cartao, use_container_width=True)

    st.markdown("<hr style='border:0; border-top:1px solid #334155; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#F8FAFC; font-size: 1.1rem; margin-bottom:5px;'>Avise os Noivos</h3>", unsafe_allow_html=True)
    
    with st.form(key=f"form_{item['id']}"):
        nome_convidado = st.text_input("Seu nome completo:", placeholder="Digite seu nome aqui...")
        if st.form_submit_button("✓ Confirme que enviou o Presente"):
            quem = nome_convidado.strip() or "Anônimo"
            dados_atuais = carregar_dados()
            for i, it in enumerate(dados_atuais["itens"]):
                if it["id"] == item["id"]:
                    dados_atuais["itens"][i]["status"] = "Alguém já nos ajudou com esse :)"
                    dados_atuais["itens"][i]["quem"] = quem
                    break
            salvar_dados(dados_atuais)
            st.success("Obrigado! Seu presente foi confirmado com sucesso. 🤍")
            st.rerun()

# ╔══════════════════════════════════════════════════════════════╗
# ║  VISÃO PÚBLICA DA LISTA (OCULTA O NOME DO CONVIDADO)         ║
# ╚══════════════════════════════════════════════════════════════╝

st.markdown(f"<div style='text-align: center; padding: 10px;'> <h1 style='color: #0B2545;'>Casinha {config['nome_casal']}</h1> <p>Escolha um dos itens para o nosso novo lar! 🏠🤍</p> </div>", unsafe_allow_html=True)

itens = dados["itens"]

if not itens:
    st.markdown("<div style='text-align:center; padding: 30px; border: 1px dashed #0B2545; border-radius: 8px;'>A lista está vazia no momento. Adicione itens no painel abaixo!</div>", unsafe_allow_html=True)
else:
    for item in itens:
        status_atual = item["status"]
        is_disponivel = status_atual in ["disponivel", "Ainda disponível :("]

        with st.container():
            st.markdown('<div class="anuncio-identificador"></div>', unsafe_allow_html=True)
            cols_item = st.columns([1.1, 2, 1])
            
            with cols_item[0]:
                if item.get("foto"):
                    st.markdown(f"<div class='img-container'><img src='data:image/jpeg;base64,{item['foto']}' width='100%'/></div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='font-size:2.5rem;text-align:center;padding-top:5px;'>🎁</div>", unsafe_allow_html=True)
                    
            with cols_item[1]:
                st.markdown(f"<h3 style='margin:0;'>{item['emoji']} {item['nome']}</h3>", unsafe_allow_html=True)
                st.markdown(f"<span style='font-weight:bold; font-size:1.2rem; color:#0B2545;'>R$ {item['preco']:.2f}</span>", unsafe_allow_html=True)
                
                if is_disponivel:
                    st.markdown(f"<br><span class='status-badge disponivel'>✨ Ainda disponível :(</span>", unsafe_allow_html=True)
                else:
                    # Exibe apenas a mensagem genérica na parte pública, ocultando o nome do convidado
                    st.markdown(f"<br><span class='status-badge confirmado'>❤️ Alguém já nos ajudou com esse :)</span>", unsafe_allow_html=True)
            
            with cols_item[2]:
                if is_disponivel:
                    st.markdown("<div style='padding-top:10px;'>", unsafe_allow_html=True)
                    if st.button("Presentear", key=f"btn_{item['id']}", use_container_width=True):
                        modal_presentear(item, config)
                    st.markdown("</div>", unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════╗
# ║  PAINEL DE CONTROLE (EXIBE OS NOMES RESERVADAMENTE)          ║
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
                st.info("Nenhum item cadastrado.")
            else:
                for idx, item in enumerate(itens):
                    c_admin = st.columns([2, 1, 2])
                    status_ajustado = "Ainda disponível :(" if item["status"] in ["disponivel", "Ainda disponível :("] else "Alguém já nos ajudou com esse :)"
                        
                    with c_admin[0]:
                        texto_item = f"**{item['nome']}** (R$ {item['preco']:.2f})"
                        # O nome do convidado aparece apenas aqui dentro do painel
                        if item.get("quem"):
                            texto_item += f"  \n🎁 *Comprado por: {item['quem']}*"
                        st.markdown(texto_item)
                    
                    with c_admin[1]:
                        if st.button("❌ Rem.", key=f"d_{item['id']}"):
                            dados["itens"].pop(idx)
                            salvar_dados(dados)
                            st.rerun()
                            
                    with c_admin[2]:
                        opcoes = ["Ainda disponível :(", "Alguém já nos ajudou com esse :)"]
                        i_padrao = opcoes.index(status_ajustado)
                        novo = st.selectbox("Status:", opcoes, index=i_padrao, key=f"s_{item['id']}")
                        
                        if novo != item["status"]:
                            dados["itens"][idx]["status"] = novo
                            if novo == "Ainda disponível :(":
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
                            "id": gerar_id(n_nome), "nome": n_nome.strip(), "preco": float(n_preco),
                            "emoji": n_emoji.strip() or "🎁", "desc": n_desc.strip(),
                            "status": "Ainda disponível :(", "quem": "", "foto": b64
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
                c_token = st.text_input("Mercado Pago Access Token (Opcional):", value=config.get("mp_access_token", ""), type="password")
                
                if st.form_submit_button("Salvar Config."):
                    dados["config"]["nome_casal"] = c_casal
                    dados["config"]["chave_pix"] = c_chave.strip()
                    dados["config"]["nome_beneficiario"] = c_nome.strip().upper()
                    dados["config"]["cidade"] = c_cidade.strip().upper()
                    dados["config"]["mp_access_token"] = c_token.strip()
                    salvar_dados(dados)
                    st.success("Configurações updated!")
                    st.rerun()
