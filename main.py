import streamlit as st  # pip install streamlit
import pandas as pd  # pip install pandas
import plotly.express as px  # pip install plotly-express
import base64  # Standard Python Module
from io import StringIO, BytesIO  # Standard Python Module
import time # for debugging
import datetime

# download the data as excel
def generate_excel_download_link(df):
    # Credit Excel: https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/5
    towrite = BytesIO()
    df.to_excel(towrite, encoding="utf-8", index=False, header=True)  # write to BytesIO buffer
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="data_download.xlsx">Download Excel File</a>'
    return st.markdown(href, unsafe_allow_html=True)

# download the plot as html
def generate_html_download_link(fig):
    # Credit Plotly: https://discuss.streamlit.io/t/download-plotly-plot-as-html/4426/2
    towrite = StringIO()
    fig.write_html(towrite, include_plotlyjs="cdn")
    towrite = BytesIO(towrite.getvalue().encode())
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download="plot.html">Download Plot</a>'
    return st.markdown(href, unsafe_allow_html=True)

# customize the page
st.set_page_config(page_title='Excel Plotter')
st.title('Excel Plotter 📈')
st.subheader('Feed me with your Excel file')

# retrive date from uploading CSV file
uploaded_file = st.file_uploader('Choose a CSV file', type='csv')
if uploaded_file:
    st.markdown('---')
    df = pd.read_csv(uploaded_file)

    # Delete Index from data frame
    # Credit : https://docs.streamlit.io/knowledge-base/using-streamlit/hide-row-indices-displaying-dataframe
    # CSS to inject contained in a string
    hide_dataframe_row_index = """
                <style>
                .row_heading.level0 {display:none}
                .blank {display:none}
                </style>
                """

        # Inject CSS with Markdown
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

    # Display an interactive table
    st.dataframe(df)

    # change rupiah to calculate number
    for i in range(0,len(df['Total Price'])) :
        df['Total Price'][i] = df['Total Price'][i].replace('Rp. ','')
        df['Total Price'][i] = df['Total Price'][i].replace(',','')
        df['Total Price'][i] = int(df['Total Price'][i])

    # change date format on Order Date
    # credit : https://www.geeksforgeeks.org/formatting-dates-in-python/
    for i in range(0,len(df['Order date'])) :
        # get number of date as integer
        date = df['Order date'][i][9:11]
        if(date[0] == '0') :
            date = date[1]
        date = int(date) 
        
        # get number of month as integer
        month = df['Order date'][i][6:7]
        if(month[0] == '0') :
            month = month[1]
        month = int(month)

        # get number of year as integer
        year = int(df['Order date'][i][0:4])
        year = int(year)

        # change format date
        fiks_date = datetime.datetime(year,month,date)
        df['Order date'][i] = fiks_date.strftime("%d %b %Y")

    # Get the value from the select box 1
    groupby_column = st.selectbox(
        'What would you like to analyse?',
        ('Order date', 'Process Status', 'Service Status'),
    )
    
    # Get the value from the select box 2
    output_column = st.selectbox(
        'What would you like to be the output column?',
        ('Total Price', 'Count')
    )

    # -- GROUP DATAFRAME
    if(output_column == 'Total Price') :
        # grouped with the sum of Total Price
        df_grouped = df.groupby(by=[groupby_column], as_index=False)[output_column].sum()
        
        # -- PLOT DATAFRAME
        fig = px.bar(
            df_grouped,
            x=groupby_column,
            y='Total Price',
            color='Total Price',
            color_continuous_scale=['red', 'yellow', 'green'],
            template='plotly_white',
            title=f'<b>Total Price by {groupby_column}</b>'
        )
    else :
        # grouped with the number of groupby_column attribute
        # credit : https://datascienceparichay.com/article/pandas-groupby-count-of-rows-in-each-group/
        df_grouped = df.groupby(by=[groupby_column], as_index=False).size()
        
        # -- PLOT DATAFRAME
        fig = px.bar(
            df_grouped,
            x=groupby_column,
            y='size',
            color='size',
            color_continuous_scale=['red', 'yellow', 'green'],
            template='plotly_white',
            title=f'<b>Size by {groupby_column}</b>'
        )
    
    # Create the Plot
    st.plotly_chart(fig)

    # -- DOWNLOAD SECTION
    st.subheader('Downloads:')
    generate_excel_download_link(df_grouped)
    generate_html_download_link(fig)
