# Griz Emissions Dashboard

This project is a web-based dashboard for visualizing emissions data. It's built with Python, using libraries such as Streamlit, Pandas, and Plotly.

## Project Structure

- `grizzemissions.py`: This is the main script that runs the dashboard. It loads the data from SIMAP output, cleans it, and creates the visualizations.
-`blurbs.csv`: This csv has source descriptions that show up when you hover bars and on the data explorer page. Update these to reflect changes in the narrative of the data. The predictions column is where I entered some predictions for the next year, which are then interpreted in the dashboard. If this column is deleted it won't break the dashboard so if there aren't new predictions or you want to remove that feature you can just delete the column.
- `emissionsnb.ipynb`: This Jupyter notebook contains code for cleaning simap output and producing static charts

## How to Run

1. Install the required Python libraries with `pip install -r requirements.txt`.
2. Run the dashboard with `streamlit run grizzemissions.py`.

## How to Host

1. Clone this Repo
2. Navigate to streamlit.io
3. Create an account and make a new app from an existing repo
4. Input grizzemissions.py as main file path
5. Deploy!

## How to Update with new data

1. Enter all available into SIMAP and go to the Results tab, calculate a table with the following settings: Footprints: Carbon, Report Type: Categories(Higher Ed), Scope 2 Method: Location Based, Normalization: None. Copy the table into a csv including headers.
2. Do the same, but change Normalization to FTE Students.
3. Save table one as total.csv and table two as per_student.csv
4. Use these tables to overwrite the current ones, and make sure they are in the same directory as grizzemissions.py, then push to github, streamlit will automatically update. Note if headers or structure of the table changes then changes will need to be made to the code.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the terms of the MIT license.