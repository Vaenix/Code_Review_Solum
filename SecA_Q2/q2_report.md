# Section A - Question B

## Question
Which models demonstrate the highest price elasticity, based on changes in `Avg_Price_EUR` vs `Units_Sold`, and how does this vary across economic conditions (`GDP_Growth` levels)?

## Method
To estimate price elasticity in a stable and interpretable way, I used a **log-log approximation** rather than raw percentage-change ratios.

For each model, I estimated the relationship:

`log(Units_Sold) ~ log(Avg_Price_EUR)`

The slope of this relationship is used as an approximate price elasticity:
- a **more negative** value indicates **stronger price sensitivity**
- a value near zero indicates weak price sensitivity
- a positive value suggests that factors other than price may be dominating the relationship (for example product mix shifts, market trends, or model upgrades)

To study the effect of macroeconomic conditions, I split `GDP_Growth` into three buckets:
- Low
- Medium
- High

and repeated the same analysis within each bucket.

## Findings

### 1. Overall price elasticity by model
The strongest negative price elasticity is observed for:

- **iX**: -1.80
- **5 Series**: -1.06
- **MINI**: -0.86

These models appear to be the most price-sensitive in the dataset, meaning higher prices are associated with lower unit sales more clearly than for the other models.

Other models such as **i4** and **X3** show weaker negative elasticity.

Some models, including **3 Series**, **X5**, and **X7**, show positive coefficients. These should not be interpreted as true upward-sloping demand. Instead, they likely reflect confounding factors such as model upgrades, changes in regional demand mix, or broader market growth occurring alongside higher prices.

### 2. Elasticity under different GDP growth conditions
The results vary across economic environments:

- **iX**
  - Low GDP growth: -0.60
  - Medium GDP growth: -3.28
  - High GDP growth: -1.55

  This suggests that iX is especially price-sensitive under medium-growth conditions.

- **5 Series**
  - Low GDP growth: +0.52
  - Medium GDP growth: -0.60
  - High GDP growth: -3.07

  The 5 Series becomes much more price-sensitive when GDP growth is high.

- **MINI**
  - Low GDP growth: -2.09
  - Medium GDP growth: +0.77
  - High GDP growth: -1.42

  MINI shows relatively strong negative elasticity in both low- and high-growth environments, but the medium-growth period appears to be influenced by other factors.

- **i4**
  - Low GDP growth: +0.91
  - Medium GDP growth: -2.02
  - High GDP growth: +0.35

  For i4, stronger price sensitivity mainly appears in the medium-growth bucket.

## Conclusion
Overall, **iX** demonstrates the highest price elasticity in the dataset, followed by **5 Series** and **MINI**.

The results also suggest that price sensitivity is not constant across macroeconomic conditions. For some models, elasticity becomes much stronger in specific GDP growth environments, indicating that economic context interacts with pricing behaviour and demand response.

In summary, the most price-sensitive models are mainly **iX**, **5 Series**, and **MINI**, while several other models appear to be driven more by product positioning or market expansion than by price alone.