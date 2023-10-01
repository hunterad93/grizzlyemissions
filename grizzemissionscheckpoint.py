import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
cleaned_totals = pd.read_csv('data/cleaned_totals.csv')
cleaned_normalized = pd.read_csv('data/cleaned_normalized.csv')


# Create a radio button for the user to select the type of data
data_type = st.sidebar.radio('Select Data Type:', ('Total', 'Per Student'))

# Depending on the user's choice, select the appropriate data
if data_type == 'Total':
    data = cleaned_totals
else:
    data = cleaned_normalized

# Create a multiselect box for the user to select the sources
# Get sources where 'source_level' = 1
default_sources = data[data['source_level'] == 1]['Source'].unique()

# Create a multiselect box for the user to select the sources with default sources
sources = st.sidebar.multiselect('Select Sources:', data['Source'].unique(), default=default_sources)
# Create a slider for the user to select the start and end year
start_year, end_year = st.slider('Select a range of years:', min_value=2015, max_value=2023, value=(2015, 2023))
# Filter the data for the selected years
data = data[(data['Fiscal Year'] >= start_year) & (data['Fiscal Year'] <= end_year)]

# Filter the data for the selected sources
data = data[data['Source'].isin(sources)]

# Aggregate data by year and scope
year_scope_totals = data.groupby(['Fiscal Year', 'Scope'])['GHG MTCDE'].sum().reset_index()

# Create an area chart for the total over time, grouped by scope
total_emissions_over_time = px.area(year_scope_totals, x='Fiscal Year', y='GHG MTCDE', color='Scope', title='Total Emissions Over Time')
st.plotly_chart(total_emissions_over_time)

# Aggregate data by source
source_totals = data.groupby('Source')['GHG MTCDE'].sum().reset_index()

# Sort data by 'GHG MTCDE' in descending order
source_totals = source_totals.sort_values('GHG MTCDE', ascending=True)

# Create a horizontal bar chart for the source contribution
fig2 = px.bar(source_totals, x='GHG MTCDE', y='Source', orientation='h', title='Source Contribution')
st.plotly_chart(fig2)