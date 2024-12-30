# Data Handling Guide - Time Series Tables

## Overview
This document provides critical information about handling time-series data tables in the Quipu AI system, specifically for analyzing public procurement data ("ReportePCBienes") across multiple time periods.

## Data Structure
- The database contains monthly tables following the pattern `ReportePCBienesYYYYMM`
- Each table represents one month of procurement data
- All tables share identical schema structure as defined in `Diccionario_Datos_Bienes.pdf`

## Important Data Handling Rules

### 1. Table Unification
When analyzing data across multiple periods, ALWAYS use UNION ALL to combine the tables into a single dataset. This approach:
- Ensures comprehensive time-series analysis
- Maintains data integrity across periods
- Enables proper trend analysis and temporal comparisons

### 2. Query Construction Guidelines
When constructing SQL queries:
- Use dynamic table selection based on the date range in question
- Apply UNION ALL between period-specific tables
- Maintain consistent column naming across unions
- Always include temporal context in aggregations

### 3. Sample Query Pattern
```sql
SELECT 
    column1, 
    column2,
    -- other columns
    COUNT(*) as total,
    SUM(amount) as sum_amount
FROM (
    SELECT * FROM ReportePCBienes202201
    UNION ALL
    SELECT * FROM ReportePCBienes202202
    -- Add additional periods as needed
) combined_data
GROUP BY column1, column2
```

## Best Practices

### Time Period Handling
1. Always consider the full time range available in the data
2. Use appropriate temporal aggregations (monthly, quarterly, yearly)
3. Include year-over-year comparisons when relevant

### Performance Optimization
1. Apply filters before UNION ALL operations
2. Use appropriate indexing strategies
3. Consider materialized views for common queries

### Data Consistency
1. Verify consistent data types across periods
2. Handle NULL values uniformly
3. Standardize date formats across all tables

## Important Context Rules for Query Generation

When generating SQL queries:
1. NEVER query individual period tables separately when analyzing trends
2. ALWAYS use UNION ALL for multi-period analysis
3. Include appropriate date range filters in subqueries
4. Maintain consistent column aliases across UNION operations

## Example Analysis Patterns

### 1. Time Series Analysis
```sql
SELECT 
    DATE_FORMAT(FECHA_PROCESO, '%Y-%m') as period,
    COUNT(*) as transaction_count,
    SUM(TOTAL) as total_amount
FROM (
    -- Use UNION ALL across all relevant period tables
) combined_data
GROUP BY DATE_FORMAT(FECHA_PROCESO, '%Y-%m')
ORDER BY period
```

### 2. Comparative Analysis
```sql
SELECT 
    YEAR(FECHA_PROCESO) as year,
    MONTH(FECHA_PROCESO) as month,
    COUNT(*) as orders,
    SUM(TOTAL) as total_amount
FROM (
    -- UNION ALL of relevant tables
) combined_data
GROUP BY YEAR(FECHA_PROCESO), MONTH(FECHA_PROCESO)
```

## Implementation Notes

1. When receiving questions about:
   - Trends
   - Time-based comparisons
   - Historical analysis
   - Aggregate statistics
   ALWAYS use UNION ALL to combine relevant period tables

2. Key metrics should be calculated across the entire dataset, not individual periods

3. Time-based filters should be applied after table unification, not before

Remember: Treat all period tables as a single continuous dataset for any analytical query.