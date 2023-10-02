import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
cleaned_totals = pd.read_csv('data/cleaned_totals.csv')
cleaned_normalized = pd.read_csv('data/cleaned_normalized.csv')
st.set_page_config(page_title='Griz Emissions', page_icon='montana_Grizzlies_logo.webp')

main_unit = 'GHG MTCDE'

page = st.sidebar.selectbox('Navigation', ('Dashboard', 'Data Explorer'))

# Create a radio button for the user to select the type of data
data_type = st.sidebar.selectbox('Aggregation', ('Total', 'Per Student'))
data_unit = st.sidebar.selectbox('Unit', ('Tons CO2 Equivalent', 'Homes Powered Equivalent'))

# Depending on the user's choice, select the appropriate data
if data_type == 'Total':
    data = cleaned_totals
else:
    data = cleaned_normalized

if data_unit == 'Homes Powered Equivalent':
    data[main_unit] = data[main_unit] * 0.126

col1, col2 = st.columns([1,3])
with col2:
    st.markdown('<style>h1{color: #660033;}</style>', unsafe_allow_html=True)
    st.title(f'Emissions {page}') 
with col1:
    st.image('montana_Grizzlies_logo.webp', width=170)







def overview(data):
    # Create a slider for the user to select the start and end year
    start_year, end_year = st.sidebar.slider('Select a range of years:', min_value=2015, max_value=2023, value=(2015, 2023))
    # Create a multiselect box for the user to select the sources with default sources
    default_sources = [source for source in data['Source'].unique() if source not in ['Fertilizer', 'Bus Travel']]
    sources = st.sidebar.multiselect('Select Sources:', data['Source'].unique(), default=default_sources)

    # Filter the data for the selected years
    data = data[(data['Fiscal Year'] >= start_year) & (data['Fiscal Year'] <= end_year)]

    # Filter the data for the selected sources
    data = data[data['Source'].isin(sources)]

    # Aggregate data by year and scope
    year_scope_totals = data.groupby(['Fiscal Year', 'Scope'])[main_unit].sum().reset_index()


    # Convert 'Fiscal Year' from int to datetime
    year_scope_totals['Fiscal Year'] = pd.to_datetime(year_scope_totals['Fiscal Year'], format='%Y')

    # Create an area chart for the total over time, grouped by scope
    total_emissions_over_time = px.area(year_scope_totals, x='Fiscal Year', y=main_unit, color='Scope', title='Emissions by Scope')
    # Reverse the order of the legend
    total_emissions_over_time.for_each_trace(lambda trace: trace.update(showlegend=True))
    total_emissions_over_time.update_layout(legend=dict(traceorder="reversed"))
    total_emissions_over_time.update_layout(yaxis_title=data_unit)

    st.markdown("""**Scope 1 are those direct emissions that are owned or controlled by an organization, 
    whereas scope 2 and 3 indirect emissions are a consequence of the activities of the organization but occur 
    from sources not owned or controlled by it. The following chart shows emissions by scope.**""")
    st.plotly_chart(total_emissions_over_time)

    # Aggregate data by source
    source_totals = data.groupby('Source')[main_unit].sum().reset_index()

    # Sort data by main_unit in descending order
    source_totals = source_totals.sort_values(main_unit, ascending=True)

    st.markdown('**Compare total emissions for each source over the time period of your choosing. The following chart shows emissions by source.**')
    # Create a horizontal bar chart for the source contribution
    fig2 = px.bar(source_totals, x=main_unit, y='Source', orientation='h', title='Emissions by Source')
    fig2.update_layout(xaxis_title=data_unit)

    st.plotly_chart(fig2)

def explorer(data):
    st.markdown('**This page gives you full access to our emissions data. Build your own graph below by using the filter pane.**')
    # Create a multiselect box for the user to select the sources with default sources
    sources = st.sidebar.multiselect('Select Sources:', data['Source'].unique())
    # Create a slider for the user to select the start and end year
    start_year, end_year = st.sidebar.slider('Select a range of years:', min_value=2015, max_value=2023, value=(2015, 2023))
    # Filter the data for the selected years
    data = data[(data['Fiscal Year'] >= start_year) & (data['Fiscal Year'] <= end_year)]
    # Filter the data for the selected sources
    data = data[data['Source'].isin(sources)]
    # Aggregate data by year and source
    year_source_totals = data.groupby(['Fiscal Year', 'Source'])[main_unit].sum().reset_index()
    # Convert 'Fiscal Year' from int to datetime
    year_source_totals['Fiscal Year'] = pd.to_datetime(year_source_totals['Fiscal Year'], format='%Y')
    # Create a line chart for the total over time, grouped by source
    total_emissions_over_time_by_source = px.line(year_source_totals, x='Fiscal Year', y=main_unit, color='Source', title='Emissions by Source Over Time')
    total_emissions_over_time_by_source.update_layout(yaxis_title=data_unit)

    st.plotly_chart(total_emissions_over_time_by_source)

if page == 'Dashboard':
    overview(data)
else:
    explorer(data)