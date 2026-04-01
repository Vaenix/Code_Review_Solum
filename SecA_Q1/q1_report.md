# Section A - Question A

## Question
How does BEV_Share growth over time (2018–2025) correlate with Units_Sold and Revenue_EUR across different regions, and which region shows the strongest transition toward electrification?

## Method
To answer this question, I first cleaned the dataset and kept the records with valid values for `Year`, `Region`, `BEV_Share`, `Units_Sold`, and `Revenue_EUR`.

Then I aggregated the data by **Year + Region**:
- `BEV_Share`: mean
- `Units_Sold`: sum
- `Revenue_EUR`: sum

For each region, I measured:
1. the trend of `BEV_Share` over time,
2. the Pearson correlation between `BEV_Share` and `Units_Sold`,
3. the Pearson correlation between `BEV_Share` and `Revenue_EUR`,
4. the total increase in `BEV_Share` from 2018 to 2025.

## Findings

### 1. BEV_Share increased in all regions
All four regions show a clear upward trend in `BEV_Share` between 2018 and 2025, indicating a consistent transition toward electrification across the global market.

The increase in BEV share is:

- China: +0.1740
- RestOfWorld: +0.1737
- Europe: +0.1736
- USA: +0.1731

This shows that **China recorded the largest overall increase in BEV share**.

### 2. Correlation with Units_Sold
The correlation between `BEV_Share` and `Units_Sold` is positive in every region:

- China: 0.958
- RestOfWorld: 0.795
- Europe: 0.844
- USA: 0.979

This suggests that increasing electrification is generally associated with stronger vehicle sales, especially in the **USA** and **China**.

### 3. Correlation with Revenue_EUR
The correlation between `BEV_Share` and `Revenue_EUR` is also positive across all regions and follows a similar pattern.

The strongest relationship is observed in the **USA**, indicating that rising BEV penetration there is closely associated with revenue growth as well.

## Conclusion
Overall, **China shows the strongest transition toward electrification** when measured by the largest increase in `BEV_Share` from 2018 to 2025.

At the same time, the **USA shows the strongest positive correlation** between `BEV_Share` and both `Units_Sold` and `Revenue_EUR`, suggesting that electrification in the U.S. market is most closely aligned with commercial performance.

In summary, the dataset indicates that BEV adoption has increased steadily across all regions, but the relationship between electrification and business outcomes is strongest in the USA, while the strongest pure adoption growth is observed in China.
## Notes
I used simple aggregation and correlation analysis to keep the solution interpretable and reproducible. The focus was on answering the business question clearly rather than using unnecessarily complex modelling.