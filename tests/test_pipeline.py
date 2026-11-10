from pipeline import generate_policies, validate, metrics

def test_reproducible_data():
    a = generate_policies()
    b = generate_policies()
    assert a.equals(b)
    assert len(a) == 1200

def test_quality_and_metrics():
    df = generate_policies()
    validate(df)
    k = metrics(df)
    assert k['policies'] == 1200
    assert 0 <= k['approval_rate'] <= 1
    assert k['submitted_claims'] >= k['approved_claims']
    assert k['total_premiums'] > 0
