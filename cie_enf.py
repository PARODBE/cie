import pandas as pd
import streamlit as st
import base64
from streamlit_option_menu import option_menu

# Título principal
st.markdown("<h1 style='text-align: center; font-size: 100px; font-style: italic; color: grey;'>Extractor de CIEs 10</h1>", unsafe_allow_html=True)

# Estilo del footer
footer_style = """
    position: fixed;
    left: 0;
    z-index: 3;
    bottom: 0;
    width: 100%;
    color: white;
    font-style: italic;
    text-align: left;
    padding: 10px;
    font-size: 16px;
"""
st.markdown(
    f'<div style="{footer_style}">Copyright (C) 2024 Pablo Rodríguez Belenguer</div>',
    unsafe_allow_html=True
)

# Manejo del estado del menú
if st.session_state.get('switch_button', False):
    st.session_state['menu_option'] = (st.session_state.get('menu_option', 0) + 1) % 2
    manual_select = st.session_state['menu_option']
else:
    manual_select = None

# Menú de navegación
selected = option_menu(None, ["Home", "Datos", "Contacto"],
                        icons=['house', "upload", "envelope-at-fill"],
                        orientation="horizontal", manual_select=manual_select, key='menu_20', menu_icon='cast', default_index=0,
                        styles={
        "container": {"padding": "21!important", "background-color": "#b4bbbf", "width": "auto"},
        "icon": {"color": "#4e5152", "font-size": "25px", "text-align": "center"},
        "nav-link": {"font-size": "25px", "text-align": "center", "margin": "15px", "--hover-color": "#757473", "font-color": "#0a0a0a"},
        "nav-link-selected": {"background-color": "#2E6E88"},
    })

# Sección de "Home"
if selected == "Home":
    st.markdown('<div style="text-align: justify; font-size: 18px; color: #696969;">Ésta aplicación web pretende obtener los códigos CIE 10 a partir de las enfermedades de forma muy sencilla y que te permita extraerlos en formato txt para su posterior uso.</div>', unsafe_allow_html=True)
    st.write('')  # Espacio adicional
    st.markdown("""<div style="text-align: center;">
        <img src="https://www.iislafe.es/media/upload/imatges/big-data-salud-digital/MARCA_ALTERNATIVA_AZUL_ACTUALIZADA.jpg" alt="IISLAFE logo" width="600">
    </div>""", unsafe_allow_html=True)

# Sección de "Datos"
elif selected == "Datos":
    st.title("Buscador de Enfermedades CIE10")

    # Cargar datos una sola vez y almacenarlos en el estado de la sesión
    if "data" not in st.session_state:
        github_csv_url = "https://raw.githubusercontent.com/PARODBE/cie/main/cie10.csv"
        st.session_state.data = pd.read_csv(github_csv_url, index_col=0)[['Código', 'Descripción', 'Nodo_Final']]
    
    # Guardar el DataFrame en una variable local
    results = st.session_state.data

    enf = st.text_input("Ingrese el nombre de la enfermedad:", value=st.session_state.get("search_term", ""))

    # Botón para realizar la búsqueda
    if st.button("Buscar Enfermedad"):
        st.session_state.search_term = enf  # Guardar el término de búsqueda
        filtered_results = results[(results.Código.str.contains(enf, case=False, na=False)) | 
                                   (results.Descripción.str.contains(enf, case=False, na=False))]

        # Almacenar los resultados filtrados en el estado de la sesión
        st.session_state["results"] = filtered_results

        # Verificar si hay resultados
        if not filtered_results.empty:
            st.data_editor(filtered_results, num_rows="dynamic")

            # Convertir el DataFrame a texto para descarga
            txt = ','.join(code.strip() for code in filtered_results['Código'].tolist())

            # Codificar el texto en base64
            b64 = base64.b64encode(txt.encode()).decode()

            # Crear el enlace para descargar el archivo de texto
            linko = f'<a href="data:file/txt;base64,{b64}" download="cies.txt">Download txt file</a>'

            # Mostrar el enlace en Streamlit
            st.markdown(linko, unsafe_allow_html=True)
        else:
            st.write("No se encontraron resultados.")

# Sección de "Contacto"
elif selected == "Contacto":
    col1, col2 = st.columns([1.25, 1])

    with col1:
        st.markdown("<h1 style='text-align: left; font-size: 30px; font-style: bold; color: #696969;'>Sobre mi</h1>", unsafe_allow_html=True)
        st.markdown('<div style="text-align: justify; font-size: 18px; color: #696969;">Mi nombre es Pablo Rodríguez Belenguer, y actualmente trabajo en la Plataforma de Big Data, IA, Bioestadística y Bioinformática de IISLAFE cuya líder del equipo es la Dra. María Eugenia Gas López. Los últimos 5 años he adquirido experiencia en ciencia de datos e IA gracias a los másters que he cursado y a mi doctorado en Biomedicina y Farmacia, el cual ha versado sobre la combinación de modelos de ML para tratar de reducir complejidades inherentes en cualquier problema de la toxicología computacional.</div>', unsafe_allow_html=True)

    with col2:
        left_container = """
        <div style="float: left; margin-right: 1rem; margin-top: 90px;">
            <img src="https://raw.githubusercontent.com/PARODBE/streamlit_figures/main/me.png" alt="Juntas" width="300" heigh="200">
        </div>
        """
        st.markdown(left_container, unsafe_allow_html=True)

    st.write('')
    st.markdown('<div style="text-align: justify; font-size: 18px; color: #696969;">Si compartes mi pasión por la IA, no dudes en contactarme y debatiremos!</div>', unsafe_allow_html=True)
    st.write('---')
    st.markdown("<h1 style='text-align: left; font-size: 30px; font-style: bold; color: #696969;'>Contact information</h1>", unsafe_allow_html=True)
    st.write('')
    st.markdown('[<img src="https://upload.wikimedia.org/wikipedia/commons/7/7e/Gmail_icon_%282020%29.svg" alt="Gmail Icon" width="30">](mailto:parodbe@gmail.com)', unsafe_allow_html=True)
    st.write('')
    st.markdown('[<img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" alt="LinkedIn Icon" width="30">](https://www.linkedin.com/in/pablorodriguezbelenguer)', unsafe_allow_html=True)
    st.write('')
    st.markdown('[<img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg" alt="GitHub Icon" width="30">](https://github.com/parodbe)', unsafe_allow_html=True)
