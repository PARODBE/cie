import pandas as pd
import streamlit as st
import csv
import base64
import requests
import io
import zipfile
from streamlit_option_menu import option_menu

st.markdown("<h1 style='text-align: center; fontSize: 100px; font-style: italic; color: grey;'>Extractor de CIEs 10</h1>", unsafe_allow_html=True)

# st.markdown("<h1 style='text-align: center; fontSize: 40px; font-style: italic; color: grey;'>Extractor de CIEs </h1>", unsafe_allow_html=True)

#footer
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

if st.session_state.get('switch_button', False):
    st.session_state['menu_option'] = (st.session_state.get('menu_option', 0) + 1) % 2
    manual_select = st.session_state['menu_option']
else:
    manual_select = None

selected = option_menu(None, ["Home", "Datos", "Contacto"],
                        icons=['house', "upload","envelope-at-fill"],
                        orientation="horizontal", manual_select=manual_select, key='menu_20', menu_icon='cast',default_index = 0,
                        styles={
        "container": {"padding": "21!important", "background-color":"#b4bbbf", "width": "auto"},
        "icon": {"color": "#4e5152", "font-size": "25px", "text-align" : "center"}, 
        "nav-link": {"font-size": "25px", "text-align": "center", "margin":"15px", "--hover-color": "#757473", "font-color":"#0a0a0a"},
        "nav-link-selected": {"background-color": "#2E6E88"},
        })

if selected == "Home":
    
    
    st.markdown('<div style="text-align: justify; fontSize: 18px; color: #696969;">Ésta aplicación web pretende obtener los códigos CIE 10 a partir de las enfermedades de forma muy sencilla y que te permita extraerlos en formato txt para su posterior uso.</div>', unsafe_allow_html=True)   
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')


    st.markdown("""
    <div style="text-align: center;">
        <img src="https://www.iislafe.es/media/upload/imatges/big-data-salud-digital/MARCA_ALTERNATIVA_AZUL_ACTUALIZADA.jpg" alt="IISLAFE logo" width="600">
    </div>
""", unsafe_allow_html=True)

elif selected == "Datos":
    # Título de la aplicación
    st.title("Buscador de Enfermedades CIE10")

    # URL del archivo ZIP en GitHub
    github_zip_url = "https://github.com/cluster311/cie10/raw/master/cie/data/cie-10.zip"

    class CIECodes:
        def __init__(self):
            self.tree = self.read_csv()

        def read_csv(self):
            # Descargar el archivo ZIP
            response = requests.get(github_zip_url)
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))

            # Extraer el archivo CSV del ZIP
            csv_file = zip_file.open("cie-10.csv")

            tree = {}
            fieldnames = ['code', 'code_0', 'code_1', 'code_2', 'code_3', 'code_4', 'description', 'level', 'source']
            
            reader = csv.DictReader(io.TextIOWrapper(csv_file, encoding='utf-8'), fieldnames=fieldnames)
            next(reader)  # Omite la fila de encabezado
            for row in reader:
                # Limpia los valores
                for k, v in row.items():
                    row[k] = v.strip().replace('–', '-')  # Reemplaza guiones largos por cortos

                code = row['code']
                
                if code in tree:
                    raise Exception(f'Duplicated code {code}')

                # Verifica los códigos dependientes
                for coden in ['code_0', 'code_1', 'code_2', 'code_3', 'code_4']:
                    rcoden = row[coden]
                    if rcoden != '' and rcoden not in tree:
                        raise Exception(f'Missing code {rcoden}')
                
                level = int(row['level'])
                tree[code] = {'description': row['description'],
                            'source': row['source'],
                            'level': level} 
                
                depends_on_field = f'code_{level-1}'
                
                if level > 0:
                    if row[depends_on_field] not in tree:
                        raise Exception(f'Parent node does not exist: {row[depends_on_field]}')
                    tree[code]['depends_on'] = row[depends_on_field]
                else:
                    tree[code]['depends_on'] = None
            
            return tree

        def info(self, code):
            if code not in self.tree:
                code = code.replace('.', '')  # W231 == W23.1
                if code not in self.tree:
                    return None
            
            ret = self.tree[code]
            descriptions = [ret['description']]
            while ret['depends_on'] is not None:
                ret = self.tree[ret['depends_on']]
                descriptions.append(ret['description'])

            ret = self.tree[code]
            ret['multiple_descriptions'] = descriptions
            ret['code'] = code
            return ret

        def search(self, txt):
            # Busca códigos que contengan el texto proporcionado
            for code, content in self.tree.items():
                full_info = self.info(code=code)
                full_str = ' '.join([str(val).lower() for key, val in full_info.items()])
                if txt.lower() in full_str:
                    yield full_info

        def search_by_disease(self, disease_name):
            # Usa el método search para buscar enfermedades
            return list(self.search(disease_name))

    def format_code(code):
        """Convierte un código, insertando un punto después del segundo número si hay más de dos, y maneja guiones."""
        # Si el código contiene un guión, lo separaremos en dos partes
        if '-' in code:
            parts = code.split('-')
            formatted_parts = [insert_period(part) for part in parts]
            return '-'.join(formatted_parts)  # Vuelve a unir las partes con un guión

        return insert_period(code)  # Formatea el código si no contiene guiones

    def insert_period(code):
        """Inserta un punto después del segundo número si hay más de dos."""
        # Encuentra la posición del primer número
        index = 1
        while index < len(code) and not code[index].isdigit():
            index += 1
        
        # Si hay más de dos números, insertar el punto
        if index + 2 < len(code):  # Verifica que haya más de dos números
            return f"{code[:index + 2]}.{code[index + 2:]}"  # Inserta el punto

        return code  # Retorna el código original si no se cumple la condición

    # Campo para ingresar la enfermedad
    enf = st.text_input("Ingrese el nombre de la enfermedad:")

    # Uso de la clase
    cie_codes = CIECodes()

    # Botón para realizar la búsqueda
    if st.button("Buscar Enfermedad"):
        # Busca por enfermedad
        results = cie_codes.search_by_disease(enf)

        results = pd.DataFrame(results)
        if not results.empty and 'source' in results.columns:
            results = results[results.source == 'icdcode.info']

        if not results.empty and 'code' in results.columns:
            results['code'] = results['code'].apply(format_code)

            st.dataframe(results)

            # Convertir el DataFrame a texto
            txt = ','.join(code.strip() for code in results['code'].tolist())

            # Codificar el texto en base64
            b64 = base64.b64encode(txt.encode()).decode()

            # Crear el enlace para descargar el archivo de texto
            linko = f'<a href="data:file/txt;base64,{b64}" download="cies.txt">Download txt file</a>'

            # Mostrar el enlace en Streamlit
            st.markdown(linko, unsafe_allow_html=True)
        else:
            st.write("No se encontraron resultados.")
elif selected == "Contacto":

    col1, col2 = st.columns([1.25,1])

    with col1:
        st.markdown("<h1 style='text-align: left; fontSize: 30px; font-style: bold; color: #696969;'>Sobre mi</h1>", unsafe_allow_html=True)
        st.markdown('<div style="text-align: justify; fontSize: 18px; color: #696969;">Mi nombre es Pablo Rodríguez Belenguer, y actualmente trabajo en la Plataforma de Big Data, IA, Bioestadística y Bioinformática de IISLAFE cuya líder del equipo es la Dra. María Eugenia Gas López. Los últimos 5 años he adquirido experiencia en ciencia de datos e IA gracias a los másters que he cursado y a mi doctorado en Biomedicina y Farmacia el cual ha versado sobre la combinación de modelos de ML para tratar de reducir complejidades inherentes en cualquier problema de la toxicología computacional.</div>', unsafe_allow_html=True)
        
    with col2:
        left_container = """
        <div style="float: left; margin-right: 1rem; margin-top: 90px;">
            <img src="https://raw.githubusercontent.com/PARODBE/streamlit_figures/main/me.png" alt="Juntas" width="300" heigh="200">
        </div>
        """
        st.markdown(left_container, unsafe_allow_html=True)
    st.write('')
    st.markdown('<div style="text-align: justify; fontSize: 18px; color: #696969;">Si compartes mi pasión por la IA no duces en contactarme y debatiremos!</div>', unsafe_allow_html=True)
    st.write('---')
    st.markdown("<h1 style='text-align: left; fontSize: 30px; font-style: bold; color: #696969;'>Contact information</h1>", unsafe_allow_html=True)
    st.write('')
    st.markdown('[<img src="https://upload.wikimedia.org/wikipedia/commons/7/7e/Gmail_icon_%282020%29.svg" alt="Gmail Icon" width="30">](mailto:parodbe@gmail.com)', unsafe_allow_html=True)
    st.write('')
    st.markdown('[<img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png" alt="LinkedIn Icon" width="30">](https://www.linkedin.com/in/pablorodriguezbelenguer)', unsafe_allow_html=True)
    st.write('')
    st.markdown('[<img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg" alt="GitHub Icon" width="30">](https://github.com/parodbe)', unsafe_allow_html=True)