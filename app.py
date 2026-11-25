import os
import streamlit as st
import pandas as pd

# 1. Configurar la página en modo ancho (Wide) desde el inicio
st.set_page_config(
    page_title="Gestión de Clientes - Lead 360",
    page_icon="📋",
    layout="wide"
)

# 2. Aplicar fondo moderno y estilos limpios con los colores solicitados
st.markdown(
    """
    <style>
    /* Fondo principal con degradado moderno y suave */
    .stApp {
        background: linear-gradient(135deg, #C7B8E7 0%, #F5C4AF 100%);
        background-attachment: fixed;
    }

    /* Hacer transparente la barra superior de Streamlit */
    header[data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0);
    }

    /* Tarjeta blanca translúcida para el contenedor principal */
    .block-container {
        background-color: rgba(255, 255, 255, 0.88);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 2.5rem 3rem;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 35px rgba(31, 38, 135, 0.12);
    }

    /* Estilo profesional para el formulario de login */
    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid rgba(199, 184, 231, 0.5);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data(ttl=1)
def cargar_datos():
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_excel = os.path.join(carpeta_actual, "datos.xlsx")
    
    df_usuarios = pd.read_excel(ruta_excel, sheet_name="Usuarios", dtype=str)
    df_clientes = pd.read_excel(ruta_excel, sheet_name="Clientes", dtype=str)
    return df_usuarios, df_clientes


df_usuarios, df_clientes = cargar_datos()
carpeta_actual = os.path.dirname(os.path.abspath(__file__))

# Control de sesión
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario_actual"] = ""
    st.session_state["rol"] = ""

# ==========================================
# PANTALLA DE LOGIN CON LOGOS A LOS LADOS
# ==========================================
if not st.session_state["autenticado"]:
    # Espaciado superior para centrar verticalmente
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Estructura de 3 columnas con alineación vertical centrada
    col_izq, col_centro, col_der = st.columns([1.2, 2, 1.2], vertical_alignment="center")
    
    # Logo Izquierdo (Lead 360)
    with col_izq:
        ruta_logo1 = os.path.join(carpeta_actual, "logo_lead360.png")
        if os.path.exists(ruta_logo1):
            st.image(ruta_logo1, use_container_width=True)
        else:
            st.info("Guarda el primer logo como 'logo_lead360.png' en la carpeta del proyecto.")

    # Formulario Central
    with col_centro:
        st.markdown(
            "<h2 style='text-align: center; color: #4A2574; margin-bottom: 1rem;'>🔒 Acceso para Vendedores</h2>",
            unsafe_allow_html=True
        )
        with st.form("login_form"):
            usuario = st.text_input("Usuario", placeholder="Ingresa tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            submit = st.form_submit_button("Ingresar", use_container_width=True, type="primary")

            if submit:
                user_match = df_usuarios[
                    (df_usuarios["Usuario"] == usuario) & 
                    (df_usuarios["Contraseña"] == password)
                ]
                if not user_match.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_actual"] = usuario
                    st.session_state["rol"] = user_match.iloc[0]["Rol"]
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

    # Logo Derecho (WOW)
    with col_der:
        ruta_logo2 = os.path.join(carpeta_actual, "logo_wow.png")
        if os.path.exists(ruta_logo2):
            st.image(ruta_logo2, use_container_width=True)
        else:
            st.info("Guarda el segundo logo como 'logo_wow.png' en la carpeta del proyecto.")

    st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# PANTALLA PRINCIPAL (LISTA DE CLIENTES)
# ==========================================
else:
    col1, col2 = st.columns([8, 1.5], vertical_alignment="center")
    with col1:
        st.title(f"📋 Lista de Clientes - Bienvenido, {st.session_state['usuario_actual']}")
    with col2:
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()

    # Filtrar clientes si no es administrador
    if st.session_state["rol"].lower() != "admin":
        clientes_visibles = df_clientes[df_clientes["Vendedor_Asignado"] == st.session_state["usuario_actual"]]
    else:
        clientes_visibles = df_clientes

    # Buscador y Segmentadores lado a lado (3 columnas)
    col_busqueda, col_filtro_cobranza, col_filtro_estado = st.columns([1.2, 1, 1])
    
    with col_busqueda:
        busqueda = st.text_input("🔍 Buscar cliente por nombre o teléfono:")
    
    with col_filtro_cobranza:
        opciones_cobranza = sorted(clientes_visibles["Cobranza"].dropna().unique().tolist())
        filtro_cobranza = st.multiselect(
            "📊 Filtrar por Cobranza:",
            options=opciones_cobranza,
            placeholder="Todas las cobranzas"
        )

    with col_filtro_estado:
        opciones_estado = sorted(clientes_visibles["Estado"].dropna().unique().tolist())
        filtro_estado = st.multiselect(
            "📌 Filtrar Estados:",
            options=opciones_estado,
            placeholder="Todos los estados"
        )

    # Aplicar filtro de Cobranza
    if filtro_cobranza:
        clientes_visibles = clientes_visibles[clientes_visibles["Cobranza"].isin(filtro_cobranza)]

    # Aplicar filtro de Estados
    if filtro_estado:
        clientes_visibles = clientes_visibles[clientes_visibles["Estado"].isin(filtro_estado)]

    # Aplicar buscador rápido
    if busqueda:
        clientes_visibles = clientes_visibles[
            clientes_visibles.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
        ]

    # Tabla grande a lo ancho y a lo alto
    st.dataframe(
        clientes_visibles,
        use_container_width=True,
        hide_index=True,
        height=650
    )
