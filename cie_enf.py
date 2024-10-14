import streamlit as st
import pandas as pd
import base64
from streamlit_option_menu import option_menu
from io import StringIO

def send_df_to_db(df):
    # Aquí podrías agregar lógica para enviar el DataFrame a una base de datos
    print(f"Nuevo dataset:\n{df}")
    st.write("Nuevo dataset:")
    st.write(df)

# Función para cargar los datos desde GitHub
def get_data():
    github_csv_url = "https://raw.githubusercontent.com/PARODBE/cie/main/cie10.csv"
    df = pd.read_csv(github_csv_url, index_col=0)[['Código', 'Descripción', 'Nodo_Final']]
    return df

# Inicializa el estado de la sesión para el DataFrame
if 'df' not in st.session_state:
    st.session_state.df = None
if 'edited_df' not in st.session_state:
    st.session_state.edited_df = None

# Título principal
st.markdown("<h1 style='text-align: center; font-size: 100px; font-style: italic; color: grey;'>Extractor de CIEs 10</h1>", unsafe_allow_html=True)

# Estilo del footer
footer_style = """
    position: fixed;
    left: 0;
    z-index: 3;
    bottom: 0;
    width: 100%;
    color: blue;
    font-style: italic;
    text-align: left;
    padding: 10px;
    font-size: 16px;
"""
st.markdown(
    f'<div style="{footer_style}">Copyright (C) 2024 Pablo Rodríguez Belenguer</div>',
    unsafe_allow_html=True
)

# Menú de navegación
selected = option_menu(None, ["Home", "Datos", "Contacto"],
                        icons=['house', "upload", "envelope-at-fill"],
                        orientation="horizontal", key='menu_20', menu_icon='cast', default_index=0)

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
    
    if st.button("Cargar datos"):
        st.write("Cargando datos...")
        st.session_state.df = get_data()
        st.session_state.edited_df = st.session_state.df.copy()  # Inicia la versión editada con los datos cargados

    if st.session_state.df is not None:
        enf = st.text_input("Ingrese el nombre de la enfermedad:", value=st.session_state.get("search_term", ""))
        
        # Filtrar resultados basados en la entrada del usuario
        filtered_results = st.session_state.edited_df[  # Cambiado a edited_df
            (st.session_state.edited_df.Código.str.contains(enf, case=False, na=False)) | 
            (st.session_state.edited_df.Descripción.str.contains(enf, case=False, na=False))
        ]
        
        if not filtered_results.empty:
            with st.form("Edit form:"):
                # Usar la versión editada del DataFrame para el editor
                edited_df = st.data_editor(filtered_results, num_rows="dynamic")
                submitted = st.form_submit_button("Ingresar dataset cambiado")
                if submitted:
                    send_df_to_db(edited_df)

                    # # Convertir el DataFrame editado a texto para descarga
                    # txt = ','.join(code.strip() for code in edited_df['Código'].tolist())

                    # # Codificar el texto en base64
                    # b64 = base64.b64encode(txt.encode()).decode()

                    # # Crear el enlace para descargar el archivo de texto
                    # linko = f'<a href="data:file/txt;base64,{b64}" download="cies.txt">Descargar un archivo tipo txt</a>'

                    # # Convertir la columna 'Código' a un formato con comillas dobles
                    # edited_df['Código'] = edited_df['Código'].apply(lambda x: f'"{x}"')

                    # # Convertir el DataFrame a un archivo CSV en formato string
                    # output = StringIO()
                    csv = edited_df[['Código','Descripción']].to_csv(index=False)
                    # edited_df[['Código','Descripción']].to_csv(output, index=False, quoting=1)  # quoting=1 asegura que los valores en comillas dobles se mantengan

                    # Obtener el texto CSV
                    b64 = base64.b64encode(csv.encode()).decode()

                    # Codificar el texto CSV en base64
                    # b64 = base64.b64encode(csv_text.encode()).decode()

                    # Crear el enlace para descargar el archivo CSV
                    linko = f'<a href="data:file/csv;base64,{b64}" download="cies.csv">Descargar un archivo tipo CSV</a>'

                    # Mostrar el enlace en Streamlit
                    st.markdown(linko, unsafe_allow_html=True)

                    # No limpiar el estado de la sesión, permitiendo volver a cargar datos
                    # st.session_state.df = None
                    # st.session_state.edited_df = None
        else:
            st.write("No se encontraron resultados.")

    else:
        st.write("No se ha cargado ningún dato")

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
