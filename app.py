"""Native Python/Streamlit application. Run: python -m streamlit run app.py."""
from pathlib import Path
import streamlit as st
from native_cartogram import build_chart, load_dataset, load_geometry

ROOT = Path(__file__).resolve().parent

@st.cache_data(show_spinner=False)
def dataset(path: str, revision: int):
    return load_dataset(Path(path))

@st.cache_data(show_spinner=False)
def geometry(path: str, revision: int, original: bool):
    return load_geometry(Path(path), original=original)

def main() -> None:
    st.set_page_config(page_title="The Affordability Gap", page_icon="🎓", layout="wide")
    st.caption("MSBA 325 · EDUCATION IN PERSPECTIVE")
    st.title("THE AFFORDABILITY GAP")
    st.subheader("How Many Months of Local Income Does a Business Master's Degree Cost?")
    st.write("A year of education carries a different burden in every country. "
             "Explore how that cost compares with average local earnings.")
    csv_path = ROOT / "Affordability_Gap_Dataset.csv.csv"
    if not csv_path.exists():
        csv_path = ROOT / "Affordability_Gap_Dataset.csv"
    try:
        frame = dataset(str(csv_path), csv_path.stat().st_mtime_ns)
    except (OSError, ValueError) as error:
        st.error(f"Could not load the project dataset: {error}")
        st.stop()
    with st.container(border=True):
        st.caption("Tuition + Living Costs")
        distort = st.checkbox("Distort map by affordability", value=False, key="distort_map")
        original = not distort
        metric_key = "total"
        path = (ROOT / "data" / "ne_50m_admin_0_countries.geojson" if original else
                ROOT / "output" / f"cartogram_{metric_key}_equal_earth.geojson")
        try:
            countries = geometry(str(path), path.stat().st_mtime_ns, original)
            chart = build_chart(countries, frame, metric_key)
        except (OSError, ValueError) as error:
            st.error(f"Could not load the Python map data: {error}")
            st.stop()
        st.altair_chart(chart, width="stretch", theme=None, key="affordability_map")
        st.caption("Teal countries are included; gray countries are outside the affordability analysis."
                   + (" Area shows geography. Tick the checkbox to compare affordability by country size." if original else
                      " Country area represents months of earnings needed for tuition plus living costs."))
    with st.expander("About the data and cartogram"):
        sample = frame.loc[frame["ISO3"].ne("RUS")]
        st.write(f"{len(sample)} countries · {int(sample['University_Count'].sum())} sampled universities. "
                 "Russia is excluded due to cartogram distortion limitations; its CSV row is unchanged.")
        st.write("Months of earnings = average annual education cost ÷ average monthly earnings. "
                 "The app uses the supplied affordability columns without changing their values. "
                 "Months express an income equivalent, not the time needed to save.")
        st.write("The distorted view uses saved, validated Python-generated contiguous cartogram polygons "
                 "in Equal Earth projected metres. Altair displays these coordinates directly with an "
                 "identity projection. The original-map view is projected from Natural Earth.")
        st.write("The Python rubber-sheet algorithm and Shapely cleanup approximate the target areas. "
                 "For tuition plus living costs, mean area error is about 0.95% and the worst error "
                 "is about 9.50%. Some short borders change. See output/VALIDATION.md.")
        st.write("Income years and definitions vary. Five countries use estimated earnings. "
                 "The university sample is not a census of national programs. The original CSV "
                 "contains source URLs, verification status and country-specific quality notes.")
        st.caption("Sources: project dataset; Natural Earth 1:50m; Dougenik, Chrisman & Niemeyer "
                   "(1985). All included countries use the same teal fill; affordability is encoded by area.")

if __name__ == "__main__":
    main()
