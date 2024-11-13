"""This is created to decide sliders' range for different filters for optimizing purposes

CREATE MATERIALIZED VIEW matteo_tef.min_max_view AS
SELECT
    'id' AS column_name,
    MIN(id) AS min_value,
    MAX(id) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'icustay_id' AS column_name,
    MIN(icustay_id) AS min_value,
    MAX(icustay_id) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'vt_hour' AS column_name,
    MIN(vt_hour) AS min_value,
    MAX(vt_hour) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'p1_value' AS column_name,
    MIN(p1_value) AS min_value,
    MAX(p1_value) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'p2_value' AS column_name,
    MIN(p2_value) AS min_value,
    MAX(p2_value) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'p3_value' AS column_name,
    MIN(p3_value) AS min_value,
    MAX(p3_value) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'p4_value' AS column_name,
    MIN(p4_value) AS min_value,
    MAX(p4_value) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'rows_pre' AS column_name,
    MIN(rows_pre) AS min_value,
    MAX(rows_pre) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'rows_post' AS column_name,
    MIN(rows_post) AS min_value,
    MAX(rows_post) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'slope_pre' AS column_name,
    MIN(slope_pre) AS min_value,
    MAX(slope_pre) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'slope_pre_normalized' AS column_name,
    MIN(slope_pre_normalized) AS min_value,
    MAX(slope_pre_normalized) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'slope_post' AS column_name,
    MIN(slope_post) AS min_value,
    MAX(slope_post) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL


SELECT
    'duration_pre' AS column_name,
    MIN(duration_pre) AS min_value,
    MAX(duration_pre) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL


SELECT
    'duration_post' AS column_name,
    MIN(duration_post) AS min_value,
    MAX(duration_post) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL


SELECT
    'gap_pre' AS column_name,
    MIN(gap_pre) AS min_value,
    MAX(gap_pre) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'gap_post' AS column_name,
    MIN(gap_post) AS min_value,
    MAX(gap_post) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL


SELECT
    'deltax' AS column_name,
    MIN(deltax) AS min_value,
    MAX(deltax) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL


SELECT
    'deltay' AS column_name,
    MIN(deltay) AS min_value,
    MAX(deltay) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'minnumberoftuples' AS column_name,
    MIN(minnumberoftuples) AS min_value,
    MAX(minnumberoftuples) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'maxdeltavt' AS column_name,
    MIN(maxdeltavt) AS min_value,
    MAX(maxdeltavt) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'maxdurationtime' AS column_name,
    MIN(maxdurationtime) AS min_value,
    MAX(maxdurationtime) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'maxdeltastart' AS column_name,
    MIN(maxdeltastart) AS min_value,
    MAX(maxdeltastart) AS max_value
FROM
    matteo_tef.tep_divided_results

UNION ALL

SELECT
    'max_steady_percentage' AS column_name,
    MIN(max_steady_percentage) AS min_value,
    MAX(max_steady_percentage) AS max_value
FROM
    matteo_tef.tep_divided_results"""