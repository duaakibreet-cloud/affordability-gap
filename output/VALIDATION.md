# Final validation — 36-country visualization

Russia is excluded from the affordability calculation, remains neutral gray, and has a geographic-area target. The original 37-row CSV is unchanged. The visualization includes 102 sampled universities in 36 countries.

The final map uses an iteration limit of 40 per metric; adaptive gain start: -1 (-1 means disabled). This is an approximate contiguous rubber-sheet cartogram with explicit polygon cleanup, not a mathematically exact area cartogram.

| View | Mean absolute area error | Worst absolute error | Within ±10% | Invalid polygons | Overlap area | Borders retained |
|---|---:|---:|---:|---:|---:|---:|
| total | 0.95% | 9.50% (HKG) | 36/36 | 0 | 0.000000% | 324/325 |
| tuition | 1.02% | 10.38% (HKG) | 35/36 | 0 | 0.000000% | 325/325 |

Area error = (achieved share of the 36 sampled country areas / target share of the 36 affordability values − 1) × 100. All statistics above are recalculated after cleanup. Original numeric values are retained in the HTML tooltips.

GEOS checks polygon validity and pairwise intersections. Invalid raw geometry is repaired on copies for before-cleanup intersection measurements. Final polygon repair and overlap removal are explicit; smaller countries have priority so microstates are retained. Shared borders are measured as coincident boundary segments longer than 100 metres, rather than merely shared vertices.

Border changes:
- total: lost [['SYR', 'ISR']]; new [['LBN', 'EGY'], ['LBN', 'JOR'], ['LBN', 'PSX'], ['MAC', 'HKG'], ['SGP', 'MYS'], ['SWE', 'DNK']].
- tuition: lost none; new [['BTN', 'BGD'], ['LBN', 'EGY'], ['LBN', 'JOR'], ['LBN', 'PSX'], ['MAC', 'HKG'], ['SGP', 'MYS'], ['SWE', 'DNK'], ['SYR', 'PSX']].

Small islands, short borders, and country outlines can be distorted. Neutral countries have geographic-area targets but may change area under the common field. This is suitable for approximate data storytelling; use the original-map toggle for location and the exact tooltips for numeric comparison.

The initial 37-country quick run had Russia errors of approximately +131% (total) and +181% (tuition). A longer adaptive run increased its total-cost error to approximately +177% and introduced more crossings. That run was stopped after the project scope changed; no claim of a completed 150-iteration run is made. Russia was then excluded at the author’s request, and both 36-country maps were recomputed from the geographic input.

Browser validation is recorded separately in browser_validation.json: local-file loading with the network offline, metric and geography toggles, all 72 country/metric tooltips, matching CSV values, neutral Russia, and a mobile viewport. Desktop and mobile screenshots are captured from the actual delivered HTML.

Source CSV SHA-256: `1cdc1b7bf315ec1fe7d08a89fcb5c781f6054ae6d344a7e94ac2e77a4d98d4eb`.
