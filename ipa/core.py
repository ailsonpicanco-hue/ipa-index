"""Water Potability Index (IPA) - reference implementation.

Additive excess index anchored on Brazilian Ordinance GM/MS 888/2021.
IPA = 0  <=>  the sample complies with every measured limit.
Missing parameters contribute nothing; the result is then a lower bound and is
reported together with its coverage C (share of total weight measured).
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.optimize import linprog

# Maximum allowable values (Ordinance GM/MS 888/2021). pH: 6.0-9.0 range. ct/ec: absence in 100 mL.
MAV = {'amonia': 1.2, 'nitrito': 1.0, 'nitrato': 10.0, 'dureza': 300, 'cloreto': 250, 'cor': 15, 'SDT': 500,
       'sulfato': 250, 'turbidez': 5.0, 'na': 200, 'al': 0.2, 'ba': 0.7, 'cd': 0.003, 'pb': 0.01, 'cu': 2.0,
       'cr': 0.05, 'fe': 0.3, 'mn': 0.1, 'ni': 0.07, 'zn': 5.0, 'hg': 0.001}
PH_RANGE = (6.0, 9.0)
MICRO = ['ct', 'ec']
ANNEX9 = ['nitrato', 'nitrito', 'ba', 'cd', 'pb', 'cu', 'cr', 'ni', 'hg']   # health-risk substances
COMPONENTS = {
    'PC': ['amonia', 'nitrito', 'nitrato', 'dureza', 'cloreto', 'cor', 'SDT', 'sulfato', 'turbidez', 'pH', 'na'],
    'MB': ['ct', 'ec'],
    'HM': ['al', 'ba', 'cd', 'pb', 'cu', 'cr', 'fe', 'mn', 'ni', 'zn', 'hg'],
}
ALL_PARAMS = [p for g in COMPONENTS.values() for p in g]
THRESHOLDS = (75.0, 150.0, 225.0)
CLASSES = ['Potable', 'Non-potable L1', 'Non-potable L2', 'Non-potable L3', 'Non-potable L4']


def excursion(df: pd.DataFrame) -> pd.DataFrame:
    """Normalised excursion x in [0, 100). NaN where the parameter was not measured.

    Upper-limit parameters: x = 100 * e / (1 + e), e = v / MAV - 1 (if v > MAV, else 0).
    pH: two-sided, e = max(6 - pH, pH - 9, 0).  Microbiology: 100 if present (1), 0 if absent (0).
    """
    X = pd.DataFrame(index=df.index)
    for p in ALL_PARAMS:
        if p not in df.columns:
            X[p] = np.nan
            continue
        v = pd.to_numeric(df[p], errors='coerce')
        if p == 'pH':
            e = np.maximum.reduce([PH_RANGE[0] - v, v - PH_RANGE[1], 0 * v])
        elif p in MICRO:
            X[p] = 100.0 * v
            continue
        else:
            e = np.where(v > MAV[p], v / MAV[p] - 1.0, 0.0)
            e = pd.Series(e, index=df.index).where(v.notna())
        X[p] = 100.0 * e / (1.0 + e)
    return X


def legal_veto(df: pd.DataFrame) -> pd.Series:
    """True if E. coli is present or any Annex 9 substance exceeds its MAV (measured values only)."""
    vt = pd.Series(False, index=df.index)
    if 'ec' in df:
        vt |= pd.to_numeric(df['ec'], errors='coerce').fillna(0) == 1
    for p in ANNEX9:
        if p in df:
            vt |= pd.to_numeric(df[p], errors='coerce').fillna(-np.inf) > MAV[p]
    return vt


def ipa(df: pd.DataFrame, weights: dict | pd.Series, thresholds=THRESHOLDS, veto=True) -> pd.DataFrame:
    """Compute IPA, components, coverage and class for every row of ``df``.

    Returns columns: IPA, IPA_PC, IPA_MB, IPA_HM, coverage, n_measured, class, partial.
    ``partial`` flags IPA = 0 with coverage < 1 ("no penalty observed (partial IPA)").
    """
    w = pd.Series(weights, dtype=float).reindex(ALL_PARAMS).fillna(0.0)
    X = excursion(df)
    measured = X.notna()
    contrib = X.fillna(0.0) * w
    out = pd.DataFrame(index=df.index)
    out['IPA'] = contrib.sum(axis=1)
    for g, ps in COMPONENTS.items():
        out[f'IPA_{g}'] = contrib[ps].sum(axis=1)
    out['coverage'] = (measured * w).sum(axis=1) / w[w > 0].sum()
    out['n_measured'] = measured.sum(axis=1)
    t1, t2, t3 = thresholds
    lev = np.select([out.IPA == 0, out.IPA <= t1, out.IPA <= t2, out.IPA <= t3], [0, 1, 2, 3], 4)
    if veto:
        lev = np.where(legal_veto(df).values & (lev < 3), 3, lev)
    out['level'] = lev
    out['class'] = [CLASSES[i] for i in lev]
    out['partial'] = (out.IPA == 0) & (out.coverage < 1)
    return out


def critic(X: pd.DataFrame) -> pd.Series:
    """CRITIC weights (Diakoulaki et al., 1995) on the excursion matrix (columns = parameters)."""
    X = X.fillna(0.0)
    rng = (X.max() - X.min()).replace(0, np.nan)
    Z = ((X - X.min()) / rng).fillna(0.0)
    s = Z.std()
    R = Z.corr().fillna(0.0)
    c = s * (1 - R).sum()
    return c / c.sum()


def entropy(X: pd.DataFrame) -> pd.Series:
    """Entropy weights (Zou et al., 2006); parameters that never exceed receive zero weight."""
    X = X.fillna(0.0)
    Y = X + 1e-9
    Pm = Y / Y.sum()
    E = -(Pm * np.log(Pm)).sum() / np.log(len(X))
    d = 1 - E
    d[X.max() == 0] = 0
    return d / d.sum()


def gp_weights(lens: dict, w_data: pd.Series, lam=0.7, margin=0.1, lo=0.05, hi=1.5, ecoli_dominant=True, tier_constraints=True) -> pd.Series:
    """Goal-programming weights for a management lens.

    lens: {tier_value: [params]}, e.g. {1.0: [...], 0.6: [...], 0.2: [...]},
          or a pd.Series of explicit weights (used as the lens target, without tier constraints).
    tier_constraints=False uses the lens values only as a target (e.g. expert weights).
    Minimises sum |w_i - t_i| with t_i = lam * lens_i + (1 - lam) * w_data_i * sum(lens),
    subject to: tier order with ``margin``; sum(w) = sum(lens); lo <= w <= hi;
    optionally w_ec >= w_c for every chemical parameter c.
    """
    if isinstance(lens, pd.Series):          # explicit values (e.g. expert weights), no tiers
        params = list(lens.index); wl = lens.astype(float); tier_constraints = False; lens = {}
    else:
        params = [p for ps in lens.values() for p in ps]
        wl = pd.Series({p: t for t, ps in lens.items() for p in ps})[params]
    tot = wl.sum()
    target = lam * wl + (1 - lam) * w_data.reindex(params).fillna(0) * tot
    n = len(params); nv = 3 * n
    c = np.r_[np.zeros(n), np.ones(2 * n)]
    Aeq, beq = [], []
    for i in range(n):
        r = np.zeros(nv); r[i] = 1; r[n + i] = -1; r[2 * n + i] = 1
        Aeq.append(r); beq.append(target.iloc[i])
    r = np.zeros(nv); r[:n] = 1; Aeq.append(r); beq.append(tot)
    Aub, bub = [], []
    tiers = sorted(lens.items(), key=lambda kv: -kv[0]) if tier_constraints else []
    for a in range(len(tiers) - 1):
        for i in tiers[a][1]:
            for j in tiers[a + 1][1]:
                r = np.zeros(nv); r[params.index(j)] = 1; r[params.index(i)] = -1
                Aub.append(r); bub.append(-margin)
    if ecoli_dominant and 'ec' in params:
        for j in params:
            if j not in MICRO:
                r = np.zeros(nv); r[params.index(j)] = 1; r[params.index('ec')] = -1
                Aub.append(r); bub.append(0.0)
    res = linprog(c, A_ub=np.array(Aub) if Aub else None, b_ub=np.array(bub) if bub else None,
                  A_eq=np.array(Aeq), b_eq=np.array(beq), bounds=[(lo, hi)] * n + [(0, None)] * (2 * n), method='highs')
    if res.status != 0:
        raise ValueError(f'goal programme infeasible: {res.message}')
    return pd.Series(res.x[:n], index=params)


def smaa(df: pd.DataFrame, weights: pd.Series, spread=0.3, draws=3000, seed=0) -> pd.DataFrame:
    """Class acceptability: probability of each class under uniform +/-spread weight perturbation."""
    rng = np.random.default_rng(seed)
    w0 = pd.Series(weights, dtype=float).reindex(ALL_PARAMS).fillna(0.0).values
    X = excursion(df).fillna(0.0).values
    vt = legal_veto(df).values
    acc = np.zeros((len(df), 5))
    t1, t2, t3 = THRESHOLDS
    for _ in range(draws):
        s = X @ (w0 * rng.uniform(1 - spread, 1 + spread, len(w0)))
        lev = np.select([s == 0, s <= t1, s <= t2, s <= t3], [0, 1, 2, 3], 4)
        lev = np.where(vt & (lev < 3), 3, lev)
        acc[np.arange(len(df)), lev] += 1
    return pd.DataFrame(acc / draws, index=df.index, columns=CLASSES)
