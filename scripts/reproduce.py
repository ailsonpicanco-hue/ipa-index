"""Reproduce the main results of the paper from the raw data using the `ipa` package.

Usage:  python scripts/reproduce.py
"""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
import ipa

df = pd.read_csv(ROOT / 'data' / 'barcarena_2018_wells.csv')
P = ipa.P23

# 1. Unsupervised (CRITIC) weights on the excursion matrix of the 23 measured parameters
X = ipa.excursion(df)[P]
w_critic = ipa.critic(X)

# 2. Goal-programming weights for each management lens (lambda = 0.7)
W = {name: ipa.gp_weights(lens, w_critic, ecoli_dominant=ipa.ECOLI_DOMINANT[name]) for name, lens in ipa.LENSES.items()}
# expert weights: explicit values used as the lens target (no tiers)
W['experts'] = ipa.gp_weights(pd.Series(ipa.EXPERTS)[P], w_critic, ecoli_dominant=True)

pub = pd.read_csv(ROOT / 'data' / 'final_weights.csv', index_col=0)
print('Lens          max|w - published|   classes [Potable, L1, L2, L3, L4]   coverage')
for name in ['experts', 'health', 'sanitation', 'treatability', 'compliance']:
    diff = (W[name].reindex(P) - pub[name].reindex(P)).abs().max()
    r = ipa.ipa(df, pub[name])             # published weights include Hg = 1.0 (not analysed) for coverage
    counts = r['class'].value_counts().reindex(ipa.CLASSES).fillna(0).astype(int).tolist()
    print(f'{name:13s} {diff:10.3f}            {counts}        {r.coverage.iloc[0]:.3f}')

acc = ipa.smaa(df, pub['health'], spread=0.3, draws=3000, seed=0)
print('SMAA +/-30% (health): stable (>= 0.95):', int((acc.max(axis=1) >= 0.95).sum()), '| ambiguous (< 0.70):', int((acc.max(axis=1) < 0.70).sum()))

# 3. Missing data: the index remains computable without metals
no_metals = df.drop(columns=[c for c in ipa.COMPONENTS['HM'] if c in df.columns])
r = ipa.ipa(no_metals, pub['health'])
print('Without metals: coverage =', round(r.coverage.iloc[0], 3), '| non-potable detected =', int((r.level > 0).sum()))
