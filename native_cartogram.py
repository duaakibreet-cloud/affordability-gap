"""Python-only data and chart pipeline. Never reads or executes the old HTML.

The validated geometry exports are planar, already area-distorted polygons.
Altair's identity projection preserves those coordinates and area ratios.
"""
import json
from pathlib import Path
import altair as alt
import numpy as np
import pandas as pd
from shapely.geometry import mapping, shape
from shapely.ops import transform

METRICS = {"total": "Total_Affordability_Months", "tuition": "Tuition_Affordability_Months"}
COLORS = ["#1a9850", "#91cf60", "#d9ef8b", "#fee08b", "#fc8d59", "#d73027", "#a50026"]
NUMERIC = ["University_Count", "Avg_Annual_Tuition_USD", "Avg_Annual_Living_USD",
           "Avg_Total_Cost_USD", "Avg_Monthly_Earnings_USD", *METRICS.values()]

def load_dataset(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, encoding="utf-8-sig")
    required = {"ISO3", "Country", *NUMERIC}
    if not required.issubset(frame.columns):
        raise ValueError(f"Missing columns: {sorted(required - set(frame.columns))}")
    if frame["ISO3"].duplicated().any():
        raise ValueError("Country ISO codes must be unique.")
    for name in NUMERIC:
        frame[name] = pd.to_numeric(frame[name], errors="raise")
    sample = frame.loc[frame["ISO3"].ne("RUS")]
    for metric in METRICS.values():
        if sample[metric].isna().any() or (sample[metric] <= 0).any():
            raise ValueError(f"Sampled countries need positive {metric} values.")
    return frame

def equal_earth(x, y, z=None):
    """Equal Earth, metres; same constants as the reference Python generator."""
    a1, a2, a3, a4 = 1.340264, -0.081106, 0.000893, 0.003796
    longitude, latitude = np.radians(x), np.radians(np.clip(y, -90, 90))
    theta = np.arcsin(np.sqrt(3) / 2 * np.sin(latitude))
    t2 = theta * theta
    t6 = t2 * t2 * t2
    radius = 6371008.7714
    px = radius * 2 * np.sqrt(3) * longitude * np.cos(theta) / (
        3 * (a1 + 3 * a2 * t2 + t6 * (7 * a3 + 9 * a4 * t2)))
    py = radius * theta * (a1 + a2 * t2 + t6 * (a3 + a4 * t2))
    return px, py

def load_geometry(path: Path, original: bool = False) -> list[dict]:
    with path.open(encoding="utf-8") as file:
        collection = json.load(file)
    countries = []
    for feature in collection["features"]:
        properties = feature["properties"]
        iso = properties.get("ADM0_A3") if original else properties["ISO3"]
        if iso == "ATA":
            continue
        geometry = feature["geometry"]
        if original:
            geometry = mapping(transform(equal_earth, shape(geometry)))
        countries.append({"iso": iso, "country": properties.get("name", properties.get("NAME", iso)),
                          "geometry": geometry})
    return countries

def chart_records(countries: list[dict], frame: pd.DataFrame, metric: str) -> list[dict]:
    if metric not in METRICS:
        raise ValueError("Unknown affordability metric")
    sample = frame.loc[frame["ISO3"].ne("RUS")].set_index("ISO3")
    missing = set(sample.index) - {c["iso"] for c in countries}
    if missing:
        raise ValueError(f"Missing sampled country geometry: {sorted(missing)}")
    records = []
    for country in countries:
        record = dict(country)
        record["sampled"] = country["iso"] in sample.index
        if record["sampled"]:
            row = sample.loc[country["iso"]]
            record.update(country=row["Country"], months=float(row[METRICS[metric]]),
                          tuition=row["Avg_Annual_Tuition_USD"], living=row["Avg_Annual_Living_USD"],
                          total=row["Avg_Total_Cost_USD"], income=row["Avg_Monthly_Earnings_USD"])
            record = {key: None if isinstance(value, (float, np.floating)) and pd.isna(value)
                      else value for key, value in record.items()}
        records.append(record)
    return records

def build_chart(countries: list[dict], frame: pd.DataFrame, metric: str) -> alt.LayerChart:
    records = chart_records(countries, frame, metric)
    def features(sampled):
        return {"type": "FeatureCollection", "features": [
            {"type": "Feature", "geometry": r["geometry"],
             "properties": {k:v for k,v in r.items() if k != "geometry"}}
            for r in records if r["sampled"] == sampled]}
    # Native GeoJSON avoids converting nested coordinates into tabular Arrow data.
    neutral = alt.Chart(alt.Data(values=features(False), format=alt.DataFormat(type="json", property="features"))).mark_geoshape(
        fill="#d6d6d6", stroke="#ffffff", strokeWidth=0.35, tooltip=False
    )
    sampled = alt.Chart(alt.Data(values=features(True), format=alt.DataFormat(type="json", property="features"))).mark_geoshape(
        stroke="#ffffff", strokeWidth=0.6
    ).encode(
        color=alt.Color("properties.months:Q", scale=alt.Scale(type="log", domain=[1, 256], range=COLORS, clamp=True),
                        legend=alt.Legend(title="Months of local earnings", orient="bottom",
                                          values=[1, 2, 4, 8, 16, 32, 64, 128, 256],
                                          gradientLength=250, titleLimit=300)),
        tooltip=[alt.Tooltip("properties.country:N", title="Country"),
                 alt.Tooltip("properties.months:Q", title="Months of earnings", format=".1f"),
                 alt.Tooltip("properties.tuition:Q", title="Annual tuition (USD)", format="$,.0f"),
                 alt.Tooltip("properties.living:Q", title="Annual living costs (USD)", format="$,.0f"),
                 alt.Tooltip("properties.total:Q", title="Annual total cost (USD)", format="$,.0f"),
                 alt.Tooltip("properties.income:Q", title="Monthly earnings (USD)", format="$,.0f")],
    )
    return (neutral + sampled).project(type="identity", reflectY=True).properties(
        height=480, background="#f6f5f0", description="Area-distorted education affordability cartogram"
    ).configure_view(stroke=None).configure_legend(
        titleColor="#12283b", labelColor="#526773", titleFontSize=12, labelFontSize=11)
