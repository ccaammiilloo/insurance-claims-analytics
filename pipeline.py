"""Deterministic synthetic insurance analytics pipeline."""
from pathlib import Path
import json
import sqlite3
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BASE = Path(__file__).resolve().parent
OUT = BASE / 'output'


def generate_policies(n=1200, seed=42):
    rng = np.random.default_rng(seed)
    regions = rng.choice(['Northeast', 'Southeast', 'Midwest', 'West'], n)
    products = rng.choice(['Auto', 'Home', 'Health', 'Life'], n, p=[.35,.25,.25,.15])
    premiums = np.round(rng.uniform(800, 3000, n), 2)
    submitted = rng.random(n) < .64
    approved = submitted & (rng.random(n) < .70)
    statuses = np.where(~submitted, 'No Claim', np.where(approved, 'Approved', 'Denied'))
    amounts = np.where(submitted, np.round(rng.uniform(500, 14000, n),2),0.)
    dates = pd.Timestamp('2025-01-01') + pd.to_timedelta(rng.integers(0,365,n),unit='D')
    return pd.DataFrame({'policy_id':[f'POL-{i:05}' for i in range(1,n+1)],'policy_date':pd.Series(dates).dt.strftime('%Y-%m-%d'), 'region':regions,'product':products,'premium_amount':premiums,'claim_status':statuses,'claim_amount':amounts})


def validate(df):
    assert len(df) > 0
    assert df.policy_id.is_unique and df.policy_id.notna().all()
    assert (df.premium_amount > 0).all()
    assert (df.claim_amount >= 0).all()
    assert set(df.claim_status).issubset({'Approved','Denied','No Claim'})
    assert (df.loc[df.claim_status=='No Claim','claim_amount']==0).all()
    assert df[['region','product','policy_date']].notna().all().all()
    pd.to_datetime(df.policy_date, format='%Y-%m-%d',errors='raise')


def metrics(df):
    submitted=int(df.claim_status.ne('No Claim').sum())
    approved=int(df.claim_status.eq('Approved').sum())
    paid=float(df.loc[df.claim_status.eq('Approved'),'claim_amount'].sum())
    premium=float(df.premium_amount.sum())
    return {'policies':int(len(df)),'total_premiums':round(premium,2),'submitted_claims':submitted,'approved_claims':approved,'approval_rate':round(approved/submitted,4) if submitted else None,'paid_claims':round(paid,2),'loss_ratio':round(paid/premium,4) if premium else None}


def write_dashboard(df, kpis, target):
    by_region=df.assign(paid_claims=np.where(df.claim_status=='Approved',df.claim_amount,0.)).groupby('region',as_index=False).agg(premiums=('premium_amount','sum'),paid_claims=('paid_claims','sum'))
    by_product=df.groupby('product',as_index=False)['premium_amount'].sum()
    status=df.claim_status.value_counts().rename_axis('claim_status').reset_index(name='count')
    fig=make_subplots(rows=2, cols=2,subplot_titles=('Premiums by region','Paid claims by region','Premiums by product','Claim status distribution'),specs=[[{'type':'bar'},{'type':'bar'}],[{'type':'bar'},{'type':'pie'}]])
    fig.add_trace(go.Bar(x=by_region.region,y=by_region.premiums,name='Premiums',marker_color='#60a5fa'),row=1,col=1)
    fig.add_trace(go.Bar(x=by_region.region,y=by_region.paid_claims,name='Paid claims',marker_color='#2dd4bf'),row=1,col=2)
    fig.add_trace(go.Bar(x=by_product['product'],y=by_product.premium_amount,name='Product premiums',marker_color='#a78bfa'),row=2,col=1)
    fig.add_trace(go.Pie(labels=status.claim_status,values=status['count'],hole=.5),row=2,col=2)
    fig.update_layout(template='plotly_dark',paper_bgcolor='#101d30',plot_bgcolor='#17283e',font_color='#e5eef9',height=850,showlegend=False,title=dict(text='Insurance Claims & Business Performance | Synthetic Portfolio Data',x=.5),margin=dict(t=100,b=65))
    cards=''.join(f'<div class="card"><div>{title}</div><strong>{value}</strong></div>' for title,value in [('Policies',f'{kpis["policies"]:,}'),('Premiums',f'${kpis["total_premiums"]:,.0f}'),('Approval Rate',f'{kpis["approval_rate"]:.1%}'),('Paid Claims',f'${kpis["paid_claims"]:,.0f}'),('Illustrative Loss Ratio',f'{kpis["loss_ratio"]:.1%}')])
    plot=fig.to_html(full_html=False,include_plotlyjs='cdn')
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Insurance Claims Analytics</title><style>body{{font-family:Arial,sans-serif;background:#101d30;color:#f2f7ff;margin:28px auto;max-width:1200px;padding:0 16px}}.cards{{display:flex;flex-wrap:wrap;gap:12px}}.card{{background:#1c304a;padding:18px 22px;border-radius:12px;flex:1;min-width:170px;color:#afc1d7}}strong{{display:block;color:white;font-size:25px;margin-top:8px}}.note{{color:#b6c6da;font-size:13px}}</style></head><body><h1>Insurance Claims &amp; Business Performance</h1><p class="note">Independent portfolio demonstration · All data synthetic · Ratios are illustrative and not actuarial estimates.</p><div class="cards">{cards}</div>{plot}</body></html>'''
    target.write_text(html,encoding='utf-8')


def run():
    OUT.mkdir(exist_ok=True)
    df=generate_policies()
    validate(df)
    df.to_csv(OUT/'policies.csv',index=False)
    with sqlite3.connect(OUT/'insurance.sqlite') as conn:
        df.to_sql('policies',conn,if_exists='replace',index=False)
    kpis=metrics(df)
    (OUT/'metrics.json').write_text(json.dumps(kpis,indent=2),encoding='utf-8')
    write_dashboard(df,kpis,OUT/'insurance_dashboard.html')
    return kpis

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
