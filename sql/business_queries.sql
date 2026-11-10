-- Insurance Claims & Business Performance Analytics
-- Synthetic portfolio data | SQLite

-- 1. Overall business KPIs
SELECT
    COUNT(*) AS total_policies,
    ROUND(SUM(premium_amount), 2) AS total_premiums,
    SUM(CASE WHEN claim_status != 'No Claim' THEN 1 ELSE 0 END) AS submitted_claims,
    SUM(CASE WHEN claim_status = 'Approved' THEN 1 ELSE 0 END) AS approved_claims,
    ROUND(SUM(CASE WHEN claim_status = 'Approved' THEN claim_amount ELSE 0 END), 2) AS paid_claims
FROM policies;

-- 2. Approval rate
SELECT
    ROUND(
        100.0 * SUM(CASE WHEN claim_status = 'Approved' THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN claim_status != 'No Claim' THEN 1 ELSE 0 END), 0),
        2
    ) AS approval_rate_pct
FROM policies;

-- 3. Insurance performance by region
SELECT
    region,
    COUNT(*) AS policies,
    ROUND(SUM(premium_amount), 2) AS premiums,
    ROUND(SUM(CASE WHEN claim_status = 'Approved' THEN claim_amount ELSE 0 END), 2) AS paid_claims,
    ROUND(
        100.0 * SUM(CASE WHEN claim_status = 'Approved' THEN claim_amount ELSE 0 END) /
        NULLIF(SUM(premium_amount), 0),
        2
    ) AS illustrative_paid_loss_ratio_pct
FROM policies
GROUP BY region
ORDER BY illustrative_paid_loss_ratio_pct DESC;

-- 4. Performance by product
SELECT
    product,
    COUNT(*) AS policies,
    ROUND(SUM(premium_amount), 2) AS total_premiums,
    SUM(CASE WHEN claim_status = 'Approved' THEN 1 ELSE 0 END) AS approved_claims
FROM policies
GROUP BY product
ORDER BY total_premiums DESC;

-- 5. Monthly premium trends
SELECT
    SUBSTR(policy_date, 1, 7) AS month,
    COUNT(*) AS policies,
    ROUND(SUM(premium_amount), 2) AS premiums
FROM policies
GROUP BY SUBSTR(policy_date, 1, 7)
ORDER BY month;
