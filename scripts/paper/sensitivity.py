"""Sensitivity and uncertainty analyses for the IPA (run after model_final.py)."""
import sys, io, json, contextlib
sys.path.insert(0, 'scripts')
with contextlib.redirect_stdout(io.StringIO()):
    import model_final as M
import numpy as np, pandas as pd
from scipy.stats import spearmanr
rng = np.random.default_rng(42)
X, P, WF, veto, viol, df = M.X, M.P, M.WF, M.veto, M.viol, M.df
Xv = X.values; vetov = veto.values; n, k = Xv.shape
ANEXO9 = M.ANEXO9

def classes(s, vt=vetov):
    c = np.select([s == 0, s <= 75, s <= 150, s <= 225], [0, 1, 2, 3], 4)
    return np.where(vt & (c < 3), 3, c)

def classes_mat(S, vt=vetov):  # S: draws x n
    c = np.select([S == 0, S <= 75, S <= 150, S <= 225], [0, 1, 2, 3], 4)
    return np.where(vt[None, :] & (c < 3), 3, c)

LENSES = ['Saude', 'Saneamento', 'Tratabilidade', 'Conformidade', 'Especialistas']
O = {}
base = {L: classes(Xv @ WF[L].values) for L in LENSES}
baseS = {L: Xv @ WF[L].values for L in LENSES}

# 1) lambda sweep and GP hyper-parameters
lams = np.round(np.arange(0, 1.0001, 0.05), 2)
sweep = {}
for L in LENSES:
    rows = []
    for lam in lams:
        w, f, _ = M.gp_lens(L, lam=lam)
        s = Xv @ w.values; c = classes(s)
        rows.append({'lam': float(lam), 'same_class_pct': round(100 * (c == base[L]).mean(), 1),
                     'rho': round(spearmanr(s, baseS[L]).statistic, 3),
                     'counts': [int((c == i).sum()) for i in range(5)], 'dev': round(f, 3)})
    sweep[L] = rows
O['lambda_sweep'] = sweep
# stable lambda range: same class >= 90% of lambda=0.7
O['lambda_stable_range'] = {L: [min(r['lam'] for r in sweep[L] if r['same_class_pct'] >= 90), max(r['lam'] for r in sweep[L] if r['same_class_pct'] >= 90)] for L in LENSES}

def gp_custom(L, lam=0.7, margin=0.1, lo=0.05, hi=1.5):
    # copy of M.gp_lens with configurable tier margin
    from scipy.optimize import linprog
    wl = M.WL[L]; tot = wl.sum(); target = lam * wl + (1 - lam) * M.wc * tot
    nn = len(P); nv = 3 * nn; c = np.r_[np.zeros(nn), np.ones(2 * nn)]
    Aeq, beq = [], []
    for i in range(nn):
        r = np.zeros(nv); r[i] = 1; r[nn + i] = -1; r[2 * nn + i] = 1; Aeq.append(r); beq.append(target.iloc[i])
    r = np.zeros(nv); r[:nn] = 1; Aeq.append(r); beq.append(tot)
    Aub, bub = [], []
    tiers = sorted(M.LENS.get(L, {}).items(), key=lambda kv: -kv[0])
    for a in range(len(tiers) - 1):
        for i in tiers[a][1]:
            for j in tiers[a + 1][1]:
                r = np.zeros(nv); r[P.index(j)] = 1; r[P.index(i)] = -1; Aub.append(r); bub.append(-margin)
    if L in ('Saude', 'Saneamento', 'Especialistas'):
        for j in M.CHEM:
            r = np.zeros(nv); r[P.index(j)] = 1; r[P.index('ec')] = -1; Aub.append(r); bub.append(0)
    res = linprog(c, A_ub=np.array(Aub) if Aub else None, b_ub=np.array(bub) if bub else None, A_eq=np.array(Aeq), b_eq=np.array(beq),
                  bounds=[(lo, hi)] * nn + [(0, None)] * (2 * nn), method='highs')
    return None if res.status != 0 else pd.Series(res.x[:nn], index=P)
hyp = {}
for L in ['Saude', 'Saneamento', 'Tratabilidade']:
    h = {}
    for m in [0.0, 0.05, 0.1, 0.2]:
        w = gp_custom(L, margin=m); h[f'margin={m}'] = None if w is None else round(100 * (classes(Xv @ w.values) == base[L]).mean(), 1)
    for hi in [1.0, 1.25, 2.0]:
        w = gp_custom(L, hi=hi); h[f'upper={hi}'] = None if w is None else round(100 * (classes(Xv @ w.values) == base[L]).mean(), 1)
    for lo in [0.0, 0.1]:
        w = gp_custom(L, lo=lo); h[f'lower={lo}'] = None if w is None else round(100 * (classes(Xv @ w.values) == base[L]).mean(), 1)
    hyp[L] = h
O['gp_hyperparameters_same_class_pct'] = hyp

# 2) Global Monte Carlo: Dirichlet weights over the whole simplex, scaled to the health-lens total
N = 20000; tot = WF['Saude'].sum()
Wd = rng.dirichlet(np.ones(k), N) * tot
Cd = classes_mat(Wd @ Xv.T)
p_severe = (Cd >= 3).mean(0); p_class = np.stack([(Cd == i).mean(0) for i in range(5)], 1)
O['dirichlet'] = {'N': N, 'p_severe_ge_0.95': int((p_severe >= 0.95).sum()), 'p_severe_le_0.05_nonpotable': int(((p_severe <= 0.05) & (base['Saude'] > 0)).sum()),
                  'modal_equals_health_pct': round(100 * (p_class.argmax(1) == base['Saude']).mean(), 1)}
# lens-centred MC with Dirichlet concentration (keeps lens priorities, alpha = 20*w/mean(w))
pc = {}
for L in LENSES:
    a = 20 * WF[L].values / WF[L].values.mean() / 1.0
    Wl = rng.dirichlet(a, 5000) * WF[L].sum(); Cl = classes_mat(Wl @ Xv.T)
    pc[L] = {'p_severe': (Cl >= 3).mean(0).round(3).tolist(), 'stable95': int(((np.stack([(Cl == i).mean(0) for i in range(5)], 1)).max(1) >= 0.95).sum())}
O['lens_mc'] = {L: {'stable95': pc[L]['stable95']} for L in LENSES}
np.save('data/p_severe_health.npy', np.array(pc['Saude']['p_severe']))
np.save('data/p_severe_global.npy', p_severe)

# 3) Sobol indices (Saltelli sampling, Jansen estimators) on weights U(0.5,1.5) x health weights
#    Output: share of samples whose class differs from the baseline health classification
Ns = 4096; wb = WF['Saude'].values
A = rng.uniform(0.5, 1.5, (Ns, k)); B = rng.uniform(0.5, 1.5, (Ns, k))
def Y(F):
    C = classes_mat((F * wb) @ Xv.T); return (C != base['Saude'][None, :]).mean(1)
def Yrho(F):
    S = (F * wb) @ Xv.T; return np.array([spearmanr(s, baseS['Saude']).statistic for s in S])
yA, yB = Y(A), Y(B); V = np.var(np.r_[yA, yB])
S1, ST = np.zeros(k), np.zeros(k)
for i in range(k):
    ABi = A.copy(); ABi[:, i] = B[:, i]; yABi = Y(ABi)
    S1[i] = np.mean(yB * (yABi - yA)) / V            # Saltelli 2010
    ST[i] = 0.5 * np.mean((yA - yABi) ** 2) / V        # Jansen
O['sobol'] = {'N': Ns, 'output': 'share of samples changing class (health lens)', 'mean_Y': round(float(np.mean(yA)) * 100, 1),
              'S1': dict(zip(P, np.round(S1, 3).tolist())), 'ST': dict(zip(P, np.round(ST, 3).tolist()))}
# bootstrap CI for Sobol ST (200 resamples of rows)
STb = []
for _ in range(200):
    idx = rng.integers(0, Ns, Ns); yAb, yBb = yA[idx], yB[idx]; Vb = np.var(np.r_[yAb, yBb]); row = []
    for i in range(k):
        ABi = A[idx].copy(); ABi[:, i] = B[idx, i]; row.append(0.5 * np.mean((yAb - Y(ABi)) ** 2) / Vb)
    STb.append(row)
STb = np.array(STb); O['sobol']['ST_ci'] = dict(zip(P, [[round(a, 3), round(b, 3)] for a, b in zip(np.percentile(STb, 2.5, 0), np.percentile(STb, 97.5, 0))]))

# 4) Alternative aggregation forms on the same data (health weights)
w = WF['Saude'].values; q = 100 - Xv  # quality score (100 = compliant)
add = Xv @ w
geo = 100 - np.exp((np.log(np.clip(q, 1e-6, None)) * w).sum(1) / w.sum())  # weighted geometric of quality, expressed as deficit
mx = (Xv * w).max(1)                                                          # worst-case (weighted max)
nviol = (Xv > 0).sum(1)
def ties(v): return int(len(v) - len(np.unique(np.round(v, 6))))
agg = {}
for name, v in [('additive', add), ('geometric', geo), ('max', mx)]:
    agg[name] = {'rho_vs_additive': round(spearmanr(v, add).statistic, 3), 'rho_vs_n_violations': round(spearmanr(v, nviol).statistic, 3),
                 'tied_values': ties(v[add > 0]), 'ecoli_in_top_quartile_pct': round(100 * (v[df.ec.values == 1] >= np.percentile(v[add > 0], 75)).mean(), 1),
                 'computable_without_metals_pct': 100.0 if name in ('additive', 'max') else 0.0}
# ambiguity check: samples with several slight exceedances (all x<50) but additive score >= a single severe exceedance (x>=90 of the top weight param)
mild = (Xv.max(1) < 50) & (nviol >= 3)
agg['ambiguity_cases'] = {'mild_multi_samples': int(mild.sum()), 'of_which_in_L3_L4_without_veto': int((mild & (base['Saude'] >= 3) & ~vetov).sum())}
O['aggregation'] = agg

# 5) Bootstrap of samples: CRITIC weight CIs and class stability with bootstrapped weights (health lens)
B_ = 500; wc_b = []; same = []
for _ in range(B_):
    idx = rng.integers(0, n, n); Xb = X.iloc[idx]; wcb = M.critic(Xb).fillna(0); wc_b.append(wcb.values)
    save = M.wc; M.wc = wcb
    try:
        wl, _, _ = M.gp_lens('Saude')
        same.append((classes(Xv @ wl.values) == base['Saude']).mean())
    except AssertionError:
        pass
    M.wc = save
wc_b = np.array(wc_b) * M.WL['Conformidade'].sum()
O['bootstrap'] = {'B': B_, 'critic_ci': dict(zip(P, [[round(a, 2), round(b, 2)] for a, b in zip(np.percentile(wc_b, 2.5, 0), np.percentile(wc_b, 97.5, 0))])),
                  'same_class_mean_pct': round(100 * np.mean(same), 1), 'same_class_p5_pct': round(100 * np.percentile(same, 5), 1)}

# 6) Analytical uncertainty: multiplicative lognormal error on concentrations (CV 10% and 20%), pH +/-0.1 / 0.2
unc = {}
for cv, dph in [(0.10, 0.1), (0.20, 0.2)]:
    D = 2000; acc = np.zeros((n, 5)); sigma = np.sqrt(np.log(1 + cv ** 2))
    for _ in range(D):
        d = df.copy()
        for kk in M.VMP: d[kk] = df[kk] * rng.lognormal(-sigma ** 2 / 2, sigma, n)
        d['pH'] = df.pH + rng.normal(0, dph, n)
        Xd = M.XN(d)
        vt = (d.ec == 1).values | np.column_stack([(d[a] > M.VMP[a]).values for a in ANEXO9]).any(1)
        c = classes(Xd.values @ WF['Saude'].values, vt); acc[np.arange(n), c] += 1
    acc /= D
    unc[f'cv{int(cv*100)}'] = {'stable95': int((acc.max(1) >= 0.95).sum()), 'modal_equals_base_pct': round(100 * (acc.argmax(1) == base['Saude']).mean(), 1),
                               'potable_flip_pct': round(100 * (1 - acc[base['Saude'] == 0, 0]).mean(), 1)}
O['analytical_uncertainty'] = unc

# 7) Leave-one-parameter-out (health lens)
loo = {}
for i, p in enumerate(P):
    w = WF['Saude'].values.copy(); w[i] = 0
    vt = vetov.copy()
    if p == 'ec': vt = np.column_stack([viol[a].values for a in ANEXO9]).any(1)
    elif p in ANEXO9: vt = viol.ec.values | np.column_stack([viol[a].values for a in ANEXO9 if a != p]).any(1)
    s = Xv @ w; c = classes(s, vt)
    loo[p] = {'class_change_pct': round(100 * (c != base['Saude']).mean(), 1), 'rho': round(spearmanr(s, baseS['Saude']).statistic, 3)}
O['leave_one_out'] = loo
json.dump(O, open('data/sensitivity.json', 'w'), ensure_ascii=False, indent=1)
short = {kk: O[kk] for kk in ['lambda_stable_range', 'gp_hyperparameters_same_class_pct', 'dirichlet', 'lens_mc', 'aggregation', 'analytical_uncertainty']}
short['bootstrap'] = {kk: O['bootstrap'][kk] for kk in ['same_class_mean_pct', 'same_class_p5_pct']}
short['sobol_top'] = sorted(O['sobol']['ST'].items(), key=lambda t: -t[1])[:8]; short['sobol_meanY'] = O['sobol']['mean_Y']
short['loo_top'] = sorted(loo.items(), key=lambda t: -t[1]['class_change_pct'])[:8]
print(json.dumps(short, ensure_ascii=False, indent=1))
for L in ['Saude']:
    print([(r['lam'], r['same_class_pct'], r['counts']) for r in sweep[L]])
