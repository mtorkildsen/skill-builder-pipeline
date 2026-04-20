---
name: analyze-sql-data
description: Analyze data using SQL queries against BigQuery, Snowflake, or PostgreSQL. Use when you need to explore datasets, generate reports, or investigate metrics in your data warehouse.
---

# Analyze SQL Data

Analyze structured data using SQL queries with support for BigQuery, Snowflake, and PostgreSQL.

## Quick start

Use SQL to query your database:

```sql
SELECT
  DATE(transaction_date) as date,
  COUNT(*) as order_count,
  SUM(total_amount) as revenue
FROM transactions
WHERE transaction_date >= '2026-01-01'
GROUP BY DATE(transaction_date)
ORDER BY date DESC;
```

Claude can:
- Write queries based on your description
- Optimize slow queries
- Debug query errors
- Explain query results

## Which database are you using?

Select your database platform for schema information and query patterns:

- **BigQuery**: See [reference/bigquery.md](reference/bigquery.md) for table schemas, BigQuery-specific functions, and optimization patterns
- **Snowflake**: See [reference/snowflake.md](reference/snowflake.md) for table definitions, Snowflake syntax, and performance tuning
- **PostgreSQL**: See [reference/postgres.md](reference/postgres.md) for schema, window functions, and extension support

If you're not sure which database you use, ask your data team or check your connection string (it usually starts with the database name).

## Common analysis patterns

### Pattern 1: Metric analysis
```sql
-- Find trending metrics
SELECT date, metric_name, metric_value
FROM metrics_log
WHERE date BETWEEN '2026-03-01' AND '2026-04-09'
ORDER BY date, metric_name;
```

### Pattern 2: Cohort analysis
```sql
-- Analyze user cohorts by signup date
SELECT
  DATE_TRUNC(signup_date, MONTH) as cohort_month,
  COUNT(DISTINCT user_id) as users_in_cohort,
  COUNT(DISTINCT CASE WHEN active_date IS NOT NULL THEN user_id END) as active_users
FROM users
GROUP BY cohort_month;
```

### Pattern 3: Funnel analysis
```sql
-- Track user journey through steps
SELECT
  step,
  COUNT(DISTINCT user_id) as user_count,
  LAG(COUNT(DISTINCT user_id)) OVER (ORDER BY step_order) as previous_step_count
FROM user_events
GROUP BY step, step_order
ORDER BY step_order;
```

## Query workflow

Follow this process for complex analyses:

1. **Describe what you're looking for**: "Show me revenue by region for Q1"
2. **Claude writes the query**: Generates SQL based on your database schema
3. **Review the query**: Verify it looks correct before running
4. **Run the query**: Execute and see results
5. **Interpret results**: Claude explains what the data shows
6. **Iterate**: Refine the query if needed

## Output formats

### For reports
Save results to CSV or JSON:
```bash
# Export query results
sqlalchemy -q "SELECT * FROM table" --format csv > output.csv
```

### For visualization
Aggregate data for charting:
```sql
SELECT date, category, COUNT(*) as count
FROM events
GROUP BY date, category
ORDER BY date;
```

Claude can create charts from aggregated data.

## Performance tips

- Index frequently-filtered columns
- Use WHERE clauses to reduce data scanned
- Aggregate before joining large tables
- Check query cost before running expensive operations

For database-specific optimization, see your database reference file (BigQuery, Snowflake, or PostgreSQL).

## Documentation

For detailed information, consult your database reference:

| Topic | Location |
|-------|----------|
| Table schemas | See `reference/[database].md` |
| Query examples | See `reference/[database].md` Examples section |
| Performance tuning | See `reference/[database].md` Optimization section |
| Troubleshooting | See `reference/[database].md` Common errors section |

Choose your database above to load the appropriate reference.

## Limitations

- Read-only queries only (no INSERT, UPDATE, DELETE)
- Large result sets may take time to process
- Some databases have query timeouts (check your reference file)
- Sensitive data should be anonymized or redacted

## When to use this skill

Invoke this skill when you:
- Need to query structured data
- Want to generate metrics or reports
- Need to investigate data quality issues
- Want to explore a dataset you're unfamiliar with
- Need help optimizing slow queries

This skill works best when you specify:
1. What database you're querying
2. What question you're trying to answer
3. Any constraints or filters needed
