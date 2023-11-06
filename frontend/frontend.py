import sys
from ast import main
from itertools import cycle
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import streamlit as st
from st_aggrid import AgGrid, DataReturnMode, GridOptionsBuilder, GridUpdateMode, JsCode

sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils import LOG

st.set_page_config(layout="wide", page_title="OpenAI PDF Translator V2")
def main():
    #File Upload
    st.sidebar.write("## Upload and download :open_file_folder:")
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    my_uploads = st.sidebar.file_uploader("Upload a PDF", type=["pdf"], accept_multiple_files=True)

    #Target Lanugage
    language = st.sidebar.radio("**Translate to:**", ("chinese","french","italian"))

    #Model Selection
    model = st.sidebar.radio("**Choose a model**", ("gpt-3.5-turbo","ChatGLM","api2d"))

    #Page number
    page_num = st.sidebar.number_input("Number of Pages", value = "min", step = 1, min_value = 0)

    #Output File Format
    ofile_ext = st.sidebar.radio("**Output file format**", ("pdf","html"))

    def translate():
        if my_uploads is None:
            raise RuntimeError("Translating but got None in uploaded file.")
        params = {
            "language": language,
            "model": model,
            "page_num": page_num,
            "file_ext": ofile_ext
        }
        file_dict = dict([(file.name, file.getvalue()) for file in my_uploads])
        LOG.info(f'Translate number of uploaded files: {len(my_uploads)}')
        response = requests.post(
            f"http://localhost:5000/translate", data=params, 
            files=file_dict, verify=False
        ) #data -> request.form ; params -> request.args
        #json_response = response.json()
        return response

    #Translate button
    if st.sidebar.button("Start Translate"):
        if my_uploads is not None:
            resp = translate()
            st.text_area(f"Translation Response: **{resp}!**")
        else:
            st.error("Fail to translate: file is None or exceeded max_file_size")

    # #Styling sidebar
    # st.sidebar.markdown("""
    #         <style>
    #         [data-testid='stSidebarUserContent'] > > div:first-child {
    #             height: 100% ;
    #         }
    #         </style>
    #         """, unsafe_allow_html=True)

    
    # Streamlit main page
    @st.cache(allow_output_mutation=True)
    def fetch_data(samples):
        deltas = cycle([
                pd.Timedelta(weeks=-2),
                pd.Timedelta(days=-1),
                pd.Timedelta(hours=-1),
                pd.Timedelta(0),
                pd.Timedelta(minutes=5),
                pd.Timedelta(seconds=10),
                pd.Timedelta(microseconds=50),
                pd.Timedelta(microseconds=10)
                ])
        dummy_data = {
            "date_time_naive":pd.date_range('2021-01-01', periods=samples),
            "apple":np.random.randint(0,100,samples) / 3.0,
            "banana":np.random.randint(0,100,samples) / 5.0,
            "chocolate":np.random.randint(0,100,samples),
            "group": np.random.choice(['A','B'], size=samples),
            "date_only":pd.date_range('2020-01-01', periods=samples).date,
            "timedelta":[next(deltas) for i in range(samples)],
            "date_tz_aware":pd.date_range('2022-01-01', periods=samples, tz="Asia/Katmandu"),
            "link": "./requirements.txt"
        }
        return pd.DataFrame(dummy_data)
    df = fetch_data(10)
    gb = GridOptionsBuilder.from_dataframe(df)
    #customize gridOptions
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
    gb.configure_column("date_only", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='yyyy-MM-dd', pivot=True)
    gb.configure_column("date_tz_aware", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='yyyy-MM-dd HH:mm zzz', pivot=True)

    gb.configure_column("apple", type=["numericColumn","numberColumnFilter","customNumericFormat"], precision=2, aggFunc='sum')
    gb.configure_column("banana", type=["numericColumn", "numberColumnFilter", "customNumericFormat"], precision=1, aggFunc='avg')
    gb.configure_column("chocolate", type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="R$", aggFunc='max')

    gridOptions = gb.build()
    grid_height = 200

    return_mode = st.sidebar.selectbox("Return Mode", list(DataReturnMode.__members__), index=1)
    return_mode_value = DataReturnMode.__members__[return_mode]

    update_mode = st.sidebar.selectbox("Update Mode", list(GridUpdateMode.__members__), index=len(GridUpdateMode.__members__)-1)
    update_mode_value = GridUpdateMode.__members__[update_mode]

    fit_columns_on_grid_load = st.sidebar.checkbox("Fit Grid Columns on Load")
    enable_enterprise_modules = st.sidebar.checkbox("Enable Enterprise Modules")

    grid_response = AgGrid(
        df, 
        gridOptions=gridOptions,
        height=grid_height, 
        width='100%',
        data_return_mode=return_mode_value, 
        update_mode=update_mode_value,
        fit_columns_on_grid_load=fit_columns_on_grid_load,
        allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
        enable_enterprise_modules=enable_enterprise_modules
        )

if __name__ == "__main__":
    main()