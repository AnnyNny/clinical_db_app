
## **Explanation of Table Parameters**

This is a description of the 33 parameters in the TEP table.

---

### **1. id** (Row ID)
Unique identifier for each row in the table.

### **2. trend_pre** (Pre-Trend)
Describes the trend before the event. Possible values:
  - `increasing`
  - `decreasing`
  - `steady`

### **3. event** (Event)
A detailed description of the event.

### **4. trend_post** (Post-Trend)
Describes the trend after the event. Possible values:
  - `increasing`
  - `decreasing`
  - `steady`

### **5. icustay_id** (ID of the ICU Stay)
Unique identifier for the ICU stay of the patient.

### **6. vt_start_pre** (Start of Pre-Trend)
Timestamp of the start of the trend before the event (`P1`).

### **7. vt_end_pre** (End of Pre-Trend)
Timestamp of the end of the trend before the event (`P2`).

### **8. vt** (Event Timestamp)
Timestamp of the event.

### **9. vt_hour** (Event Hour)
Hour of the event (e.g., if the event occurred at `12:10:15`, this field will be `12`).

### **10. vt_start_post** (Post-Trend Start)
Timestamp of the start of the post-trend (`P3`).

### **11. vt_end_post** (Post-Trend End)
Timestamp of the end of the post-trend (`P4`).

### **12. p1_value** (Value of Point 1)
Value of the parameter measured at `P1`.

### **13. p2_value** (Value of Point 2)
Value of the parameter measured at `P2`.

### **14. p3_value** (Value of Point 3)
Value of the parameter measured at `P3`.

### **15. p4_value** (Value of Point 4)
Value of the parameter measured at `P4`.

### **16. rows_pre** (Number of Rows Before Event)
Number of data points in the Pre-Trend.

### **17. rows_post** (Number of Rows After Event)
Number of data points in the Post-Trend.

### **18. slope_pre** (Pre-Slope)
Incline in the Pre-Trend between `P1` and `P2`, normalized by `P1`:

### **19. slope_pre_normalized** (Pre-Slope Normalized)
Normalized change in the Pre-Trend between `P1` and `P2`.

### **20. slope_post** (Post-Slope)
Incline in the Post-Trend between `P3` and `P4`.

### **21. duration_pre** (Duration Before Event)
Duration of the Pre-Trend.

### **22. duration_post** (Duration After Event)
Duration of the Post-Trend.

### **23. gap_pre** (Gap Before Event)
Difference between `P2` and `P1` values.

### **24. gap_post** (Gap After Event)
Difference between `P4` and `P3` values

### **25. deltax** (Delta X)
Delta X

### **26. deltay** (Delta Y)
The maximum allowed deviation of data points from their ideal position on the trend line.


### **27. minnumberoftuples** (Minimum Number of Tuples)
The minimum number of tuples required to form a valid trend:
  - Ensures better-defined trends than just two points.

### **28. maxdeltavt** (Max Delta VT)
Maximum time difference between adjacent tuples to belong to the same trend. 
This is useful to avoid those measures that are
taken too far away one from the other, becoming irrelevant to the trend itself.

### **29. maxdeltastart** (Max Delta Start)
Maximum time difference between a trend's start and the associated event.

### **30. maxdurationtime** (Max Duration Time)
Maximum allowed duration of a trend. It is particularly useful when the goal is to extract
 trends for testing the short-term effects of a certain event.

### **31. max_steady_percentage** (Max Steady Percentage)
Maximum percentage for a trend to be classified as `steady`.

### **32. influenced_by_event** (Influenced By Event)
Indicates if the trend is influenced by the event (`true` or `false`).

### **33. measure** (Measure)
Name of the table or parameter being analyzed (e.g., `tep_hr_label` for Heart Rate).

---

### **Additional Notes:**

- Visualize plots to explore how each parameter influences the trends and correlated event.
