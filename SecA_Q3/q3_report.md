# Section A - Question C

## Question
Can we identify seasonal patterns (Month-level trends) in `Revenue_EUR` and `Units_Sold`, and do these patterns interact differently with regional economic indicators (`GDP_Growth`, `Fuel_Price_Index`)?

## Method
To answer this question, I cleaned the dataset and kept rows with valid values for:
- `Month`
- `Region`
- `Units_Sold`
- `Revenue_EUR`
- `GDP_Growth`
- `Fuel_Price_Index`

Then I aggregated the data at the **Region + Month** level and calculated:
- total `Units_Sold`
- total `Revenue_EUR`
- average `GDP_Growth`
- average `Fuel_Price_Index`

I also created an overall month-level summary across all regions to identify broad seasonal patterns.

To study interaction with macroeconomic conditions, I computed the regional correlations between:
- `Units_Sold` and `GDP_Growth`
- `Units_Sold` and `Fuel_Price_Index`
- `Revenue_EUR` and `GDP_Growth`
- `Revenue_EUR` and `Fuel_Price_Index`

## Findings

### 1. Month-level seasonal patterns exist
The monthly aggregation shows that both `Units_Sold` and `Revenue_EUR` vary across months rather than remaining flat. This indicates the presence of month-level seasonal patterns in the sales data.

The months with the highest and lowest values differ, which suggests that BMW sales and revenue are influenced by seasonal demand cycles.

### 2. Revenue and sales move together, but not perfectly
In general, the month-level pattern of `Revenue_EUR` is broadly similar to that of `Units_Sold`, which is expected because higher sales volume usually contributes to higher revenue.

However, the patterns are not perfectly identical, which suggests that pricing mix and model composition may also influence revenue in addition to pure sales volume.

### 3. Seasonal patterns vary by region
When comparing the monthly curves across regions, the patterns are similar in broad direction but not identical in shape or intensity. This suggests that seasonality is not uniform across all markets.

Some regions show stronger month-to-month fluctuations than others, indicating regional heterogeneity in demand timing.

### 4. Interaction with GDP growth and fuel price differs across regions
The regional correlation analysis shows that the relationship between monthly performance and macroeconomic indicators is not constant across regions.

In general:
- `GDP_Growth` tends to show a positive relationship with `Units_Sold` and `Revenue_EUR`
- `Fuel_Price_Index` shows a more mixed relationship, with the strength and direction varying by region

This suggests that macroeconomic context interacts with seasonal sales patterns differently across regional markets.

## Conclusion
Yes, the dataset shows clear month-level seasonal patterns in both `Units_Sold` and `Revenue_EUR`.

These patterns are not identical across regions, and their relationship with `GDP_Growth` and `Fuel_Price_Index` also varies by market. Therefore, seasonality exists, but it interacts with regional economic conditions in different ways depending on the region.

Overall, the analysis suggests that BMW’s monthly commercial performance is influenced by both seasonal demand timing and region-specific macroeconomic conditions.