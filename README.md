# Griz Emissions Dashboard

This project is a web-based dashboard for visualizing emissions data. It's built with Python, using libraries such as Streamlit, Pandas, and Plotly. It's configured for both Heroku hosting with `Procfile` + `setup.sh` and for running on streamlit with the `config.toml`. This dashboard can be easily adapted to work with [SIMAP](https://unhsimap.org/home) output. SIMAP is a commonly used sustainability reporting tool for Universities.

To view the current version of the dashboard, visit [Griz Emissions Dashboard](https://griz-emissions.streamlit.app/). This link provides direct access to the live dashboard, showcasing the latest emissions data visualizations.

![Dashboard Screenshot](dashboard%20screenshot.png)


## Project Structure

- Note that everything is kept in a single directory, this project was built to be updated with new data by folks without coding experience so the hope was that using a single directory would make the update instructions below less likely to lead to the dashboard breaking.

- `grizzemissions.py`: This is the main script that runs the dashboard. It loads the data from [SIMAP](https://unhsimap.org/home) output, cleans + restructures it, and creates the visualizations.

- `emissionsnb.ipynb`: This Jupyter notebook contains code for cleaning simap output and producing static charts used in our finalized emissions report to the University of Montana.

## How to Host

1. Clone this Repo
2. Navigate to streamlit.io
3. Create an account and make a new app from an existing repo
4. Input grizzemissions.py as main file path
5. Deploy!

## How to Update Dashboard Data Source

1. Enter all available into SIMAP and go to the Results tab, calculate a table with the following settings: Footprints: Carbon, Report Type: Categories(Higher Ed), Scope 2 Method: Location Based, Normalization: None. Copy the table into a csv including headers.
2. Do the same, but change Normalization to FTE Students.
3. Save table one as total.csv and table two as per_student.csv
4. Use these tables to overwrite the current ones, and make sure they are in the same directory as grizzemissions.py, then push to github, streamlit will automatically update. Note if headers or structure of the table changes then changes will need to be made to the code.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the terms of the MIT license.