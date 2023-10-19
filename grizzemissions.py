import streamlit as st
import pandas as pd
import plotly.express as px
import os
port = int(os.environ.get("PORT", 8501))

def clean_data(totals_data_path, per_student_data_path, main_unit):
    # Load the data
    totals_data = pd.read_csv(totals_data_path)
    per_student_data = pd.read_csv(per_student_data_path)

    # Convert 'Scope' to string
    totals_data['Scope'] = totals_data['Scope'].astype(str)
    per_student_data['Scope'] = per_student_data['Scope'].astype(str)

    # Select relevant columns
    totals_data = totals_data[['Fiscal Year', 'Scope', 'Source', main_unit]]
    per_student_data = per_student_data[['Fiscal Year', 'Scope', 'Source', main_unit]]

    # Convert main_unit column to float
    # Check if main_unit column is a string, if so remove commas and convert to float
    if totals_data[main_unit].dtype == 'object':
        totals_data[main_unit] = totals_data[main_unit].str.replace(',', '').astype(float)
    if per_student_data[main_unit].dtype == 'object':
        per_student_data[main_unit] = per_student_data[main_unit].str.replace(',', '').astype(float)

    # Combine sources
    def combine_sources(source):
        if isinstance(source, str):
            if 'commuting' in source.lower():
                return 'Commuting'
            elif 'co-gen' in source.lower():
                return 'Co-gen Plant'
            else:
                return source
        else:
            return source

    totals_data['Source'] = totals_data['Source'].apply(combine_sources)
    per_student_data['Source'] = per_student_data['Source'].apply(combine_sources)

    # Sum up the 'Commuting' rows for each year
    totals_data = totals_data.groupby(['Fiscal Year', 'Scope', 'Source'], as_index=False)[main_unit].sum()
    per_student_data = per_student_data.groupby(['Fiscal Year', 'Scope', 'Source'], as_index=False)[main_unit].sum()

    # Replace source names in both dataframes
    replacements = {
        'Fertilizer & Animals': 'Fertilizer',
        'Co-gen steam': 'Co-gen Plant',
        'Direct Transportation': 'University Fleet',
        'Other On-Campus Stationary': 'Propane & Natural Gas',
        'Directly Financed Air Travel': 'Air Travel',
        'Solid Waste': 'Landfill Waste',
        'Other Directly Financed Travel': 'Bus Travel'
    }

    totals_data['Source'] = totals_data['Source'].replace(replacements)
    per_student_data['Source'] = per_student_data['Source'].replace(replacements)

    return totals_data, per_student_data, main_unit

cleaned_totals, cleaned_per_student, main_unit = clean_data('total.csv', 'per_student.csv', 'GHG MTCDE')

st.set_page_config(page_title='Griz Emissions', page_icon='logo.png')

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

page = st.sidebar.selectbox('Navigation', ('Dashboard', 'Data Explorer'))

# Create a radio button for the user to select the type of data
data_type = st.sidebar.selectbox('Aggregation', ('Total', 'Per Student'))
data_unit = st.sidebar.selectbox('Unit', ('Tons CO2 Equivalent', 'Homes Powered Equivalent'))

# Depending on the user's choice, select the appropriate data
if data_type == 'Total':
    data = cleaned_totals
else:
    data = cleaned_per_student

if data_unit == 'Homes Powered Equivalent':
    data[main_unit] = data[main_unit] * 0.126

col1, col2 = st.columns([1,3])
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<style>h1{color: #5E001D;}</style>', unsafe_allow_html=True)
    st.title(f'Emissions {page}') 
with col1:

    st.image('logo.png', width=170)
   



def overview(data):
    # Define color mapping for scopes
    color_mapping = {
        '1': '#73B7ED',  # light blue
        '2': '#0068C9',  # dark blue
        '3': '#FFABAB'   # light red
    }
    # Create a multiselect box for the user to select the sources with default sources
    default_sources = [source for source in data['Source'].unique() if source not in ['Fertilizer', 'Bus Travel', 'Propane & Natural Gas']]
    sources = st.sidebar.multiselect('Select Sources:', data['Source'].unique(), default=default_sources)

    # Filter the data for the selected sources
    data = data[data['Source'].isin(sources)]

    # Aggregate data by year and scope
    year_scope_totals = data.groupby(['Fiscal Year', 'Scope'])[main_unit].sum().reset_index()

    # Convert 'Fiscal Year' from int to datetime
    year_scope_totals['Fiscal Year'] = pd.to_datetime(year_scope_totals['Fiscal Year'], format='%Y')

    # Create an area chart for the total over time, grouped by scope
    total_emissions_over_time = px.area(year_scope_totals, x='Fiscal Year', y=main_unit, color='Scope', title='Emissions by Scope',color_discrete_map=color_mapping)
    # Reverse the order of the legend
    total_emissions_over_time.for_each_trace(lambda trace: trace.update(showlegend=True))
    total_emissions_over_time.update_layout(legend=dict(traceorder="reversed"))
    total_emissions_over_time.update_layout(yaxis_title=data_unit)
    

    st.markdown("""**Scope 1 are those direct emissions that are owned or controlled by an organization, 
    whereas scope 2 and 3 indirect emissions are a consequence of the activities of the organization but occur 
    from sources not owned or controlled by it. The following chart shows emissions by scope.**""")
    st.plotly_chart(total_emissions_over_time)

    st.markdown('**Compare total emissions for each source in a given year. The following chart shows emissions by source.**')

    col1, col2 = st.columns([1,5])
    # Create a selectbox for the user to select the year
    year = col1.selectbox('Select a year:', sorted(data['Fiscal Year'].unique(), reverse=True))
    # Filter the data for the selected year
    data = data[data['Fiscal Year'] == year]

    # Aggregate data by source
    #Aggregate data by source and scope
    source_totals = data.groupby('Source').agg({main_unit: 'sum', 'Scope': 'first'}).reset_index()
    # Sort data by main_unit in descending order
    source_totals = source_totals.sort_values(main_unit, ascending=False)
    # Load blurbs from csv
    blurbs = pd.read_csv('blurbs.csv')

    # Merge source_totals with blurbs on 'Source'
    source_totals = pd.merge(source_totals, blurbs[['Source', 'Blurb']], on='Source', how='left')

    def insert_line_breaks(text, x):
        lines = []
        line = ""
        for word in text.strip().split():  # Strip leading and trailing whitespace
            if len(line + word) > x:
                lines.append(line)
                line = word.strip()  # Remove leading spaces
            else:
                line = line + " " + word if line else word
        lines.append(line)
        # Calculate the length of the longest line
        max_length = max(len(line) for line in lines)
        # Add whitespace at the end of each line to make it equal to the length of the longest line
        lines = [line + " " * (max_length - len(line)) for line in lines]
        # Insert line breaks using the br tag
        return '<br>'.join(lines)

    # Apply the function to the 'Blurb' column
    source_totals['Blurb'] = source_totals['Blurb'].apply(lambda text: insert_line_breaks(text, x=50))

    # Create a horizontal bar chart for the source contribution
    fig2 = px.bar(source_totals, x=main_unit, y='Source', orientation='h', title=f'Emissions by Source {year}', color='Scope', color_discrete_map=color_mapping, opacity=.7,
                category_orders={"Source": list(source_totals['Source'])}, custom_data=['Blurb'])

    # Set hovertemplate to display 'Blurb' data
    fig2.update_traces(hovertemplate='%{customdata[0]}<extra></extra>')
    fig2.update_layout(hoverlabel=dict(font_size=16))
    fig2.update_layout(xaxis_title=data_unit)
    # Reverse the order of the legend
    # Update the legend order to 3, 2, 1
    def update_legend_order(trace):
        if trace.name == '1':
            trace.legendrank = 3
        elif trace.name == '2':
            trace.legendrank = 2
        elif trace.name == '3':
            trace.legendrank = 1
    fig2.for_each_trace(update_legend_order)

    st.plotly_chart(fig2)

def explorer(data):
    st.markdown("""**This page gives you full access to our emissions data. Build your own graph below by using the filter pane. 
                    Each time you select a source an informational caption will appear below the chart.**""")
    # Create a multiselect box for the user to select the sources with default sources
    sources = st.sidebar.multiselect('Select Sources:', data['Source'].unique())
    # Create a slider for the user to select the start and end year
    min_year = int(data['Fiscal Year'].min())
    max_year = int(data['Fiscal Year'].max())
    start_year, end_year = st.sidebar.slider('Select a range of years:', min_value=min_year, max_value=max_year, value=(min_year, max_year))
    # Filter the data for the selected years
    data = data[(data['Fiscal Year'] >= start_year) & (data['Fiscal Year'] <= end_year)]
    # Filter the data for the selected sources
    data = data[data['Source'].isin(sources)]
    # Aggregate data by year and source
    year_source_totals = data.groupby(['Fiscal Year', 'Source'])[main_unit].sum().reset_index()
    # Convert 'Fiscal Year' from int to datetime
    year_source_totals['Fiscal Year'] = pd.to_datetime(year_source_totals['Fiscal Year'], format='%Y')
    # Create a line chart for the total over time, grouped by source
    total_emissions_over_time_by_source = px.line(year_source_totals, x='Fiscal Year', y=main_unit, color='Source', title=f'Emissions by Source {start_year} to {end_year}')
    total_emissions_over_time_by_source.update_layout(yaxis_title=data_unit)
    # Calculate the range of years
    year_range = end_year - start_year

    # Set dtick value based on the range of years
    if year_range > 20:
        dtick_value = "M60"  # 5 years interval
    elif year_range > 8:
        dtick_value = "M24"  # 2 years interval
    else:
        dtick_value = "M12"  # 1 year interval

    total_emissions_over_time_by_source.update_xaxes(
        dtick=dtick_value,
        tickformat="%Y"  # only display year
    )

    st.plotly_chart(total_emissions_over_time_by_source)

    # Filter the data for the last selected source
    last_selected_source = sources[-1] if sources else None
    if last_selected_source:

        # Load blurbs from csv
        blurbs = pd.read_csv('blurbs.csv')

        # Get blurb for the last selected source
        source_blurb = blurbs[blurbs['Source'] == last_selected_source]['Blurb'].values[0]

        # Check if 'Percent Change Predicted' column exists
        if 'Percent Change Predicted' in blurbs.columns:
            # Get the 'Percent Change Predicted' for the last selected source
            percent_change_predicted = blurbs[blurbs['Source'] == last_selected_source]['Percent Change Predicted'].values[0]
            
            # Add prediction to the blurb based on the 'Percent Change Predicted'
            if abs(percent_change_predicted) >= 10:
                prediction = "increase" if percent_change_predicted > 0 else "decrease"
                prediction_color = "red" if percent_change_predicted > 0 else "green"
            else:
                prediction = "remain stable"
                prediction_color = "blue"
            st.markdown(f"""**{source_blurb}** <br><br> Exponential smoothing model predicts {last_selected_source.lower()} emissions will 
                        <span style='color:{prediction_color}'>{prediction}</span> for next year.""", unsafe_allow_html=True)
        else:
            # If 'Percent Change Predicted' column does not exist, just display the source blurb
            st.markdown(f"**{source_blurb}**")

if page == 'Dashboard':
    overview(data)
else:
    explorer(data)