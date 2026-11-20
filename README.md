# THE AFFORDABILITY GAP

A native Python + Streamlit visualization for the AUB MSBA Data Visualization
project, *The Master's Degree Dilemma: Is It Worth the Price?*

The app starts with an undistorted world map. Tick **Distort map by affordability**
to resize countries approximately in proportion to the months of local earnings
needed for one year of a business master's education. The only cost view is
**Tuition + Living Costs**. All 36 included countries share one teal fill, so
area—not a color scale—communicates affordability in the distorted view.
Included countries provide interactive hover details;
neutral countries have no affordability tooltip.

## Run locally

Use Python 3.12 or later and run these commands from the repository directory:

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://localhost:8501. Keep the terminal running while using the app.

## Deploy to Streamlit Community Cloud

1. Upload the **contents of this directory** to your GitHub repository, preserving
   `.streamlit/`, `data/`, and `output/` and their filenames.
2. In Streamlit Community Cloud, create an app from that repository.
3. Select `app.py` as the main file and a Python version compatible with the
   dependencies (Python 3.12 or later).
4. Deploy. No API keys or secrets are required.

All data needed by the app is included. Nothing is downloaded during app startup.
If you retain this directory as a subfolder in GitHub instead, use
`github_affordability_gap/app.py` as the main file; placing its contents at the
repository root is recommended so Streamlit reads the included theme configuration.

## Data and method

The source CSV contains 37 countries and 104 sampled universities and is unchanged.
The visualization includes 36 countries and 102 universities. Russia is excluded
because of cartogram distortion limitations and remains neutral gray.

Affordability months = annual tuition plus annual living expenses divided by
average monthly earnings. The supplied affordability values are used unchanged.
Income years, earnings definitions and source quality vary; the CSV includes
original source URLs and quality notes. Months represent an income equivalent,
not the time needed to save. The university sample is not a census of national
programs.

Pandas loads the data; NumPy and Shapely handle the original-map projection.
Altair renders the validated cartogram coordinates using an identity projection,
preserving the existing area distortion rather than displaying a regular
choropleth. Precomputed geometry comes from a Python rubber-sheet cartogram with
polygon cleanup. Mean absolute total-cost area error is approximately 0.95%; the
largest error is approximately 9.50%. Border changes and validation limits are
documented in `output/VALIDATION.md` and the validation CSV/JSON files.

Natural Earth 1:50m supplies the geographic boundaries. Cartogram method:
Dougenik, Chrisman & Niemeyer (1985), DOI: 10.1111/j.0033-0124.1985.00075.x.

This deployment contains native Python source and data only. It does not embed
HTML or depend on a separate standalone visualization file.
