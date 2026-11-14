import sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon, Wedge, FancyArrowPatch, Ellipse, Arc
lang = sys.argv[1]; pt = lang == 'pt'
INK = '#1f2328'; MUT = '#5b5f66'; BG = 'white'
BLUE = '#2a78d6'; ORA = '#eb6834'; AQ = '#1baf7a'; YEL = '#eda100'; VIO = '#6250d6'; GRY = '#8a8984'
SEV = ['#1baf7a', '#f0915f', '#d9602f', '#a8431d', '#6e2a10']
plt.rcParams['font.family'] = 'DejaVu Sans'
fig = plt.figure(figsize=(12, 7.4), facecolor=BG); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 120); ax.set_ylim(0, 74); ax.axis('off'); ax.set_aspect('equal')
T = lambda a, b: a if pt else b

def panel(x, y, w, h, num, title, col):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.25,rounding_size=1.6', fc='#f7f8fa', ec='#d6d9de', lw=1.2))
    ax.add_patch(Circle((x + 2.6, y + h - 2.6), 1.75, fc=col, ec='none'))
    ax.text(x + 2.6, y + h - 2.6, num, ha='center', va='center', color='white', fontsize=12, fontweight='bold')
    ax.text(x + 5.2, y + h - 2.6, title, ha='left', va='center', color=INK, fontsize=12.5, fontweight='bold')

def arrow(a, b, col=GRY, lw=2.2, rad=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=18, color=col, lw=lw, connectionstyle=f'arc3,rad={rad}'))

# ---------------- Panel 1: evidence (review)
panel(1, 40, 27, 32, '1', T('Revisão PRISMA', 'PRISMA review'), BLUE)
for k in range(3):
    ax.add_patch(FancyBboxPatch((4 + k * 1.3, 53.0 - k * 1.3), 9, 10.0, boxstyle='round,pad=0.1,rounding_size=0.4', fc='white', ec='#9aa3ad', lw=1))
for i in range(4):
    ax.plot([5.8 + 2.6, 5.8 + 2.6 + 6.2 - (i % 2) * 2], [58.4 - 2.6 - i * 1.4] * 2, color='#c3c9d0', lw=1.6)
ax.add_patch(Circle((14.6, 53.6), 2.9, fc='white', ec=INK, lw=2.4)); ax.plot([16.7, 18.8], [51.5, 49.4], color=INK, lw=3.2, solid_capstyle='round')
ax.text(21, 61.5, '370', fontsize=20, fontweight='bold', color=BLUE, ha='center')
ax.text(21, 58.4, T('estudos', 'studies'), fontsize=10.5, color=MUT, ha='center')
for j, (v, lab) in enumerate([(2.2, T('tratam dados faltantes', 'treat missing data')), (1.4, T('graduam a gravidade', 'grade severity'))]):
    yy = 45.4 - j * 3.6
    ax.add_patch(Rectangle((4, yy), 22, 1.7, fc='#e6e9ed', ec='none')); ax.add_patch(Rectangle((4, yy), 22 * v / 20, 1.7, fc=ORA, ec='none'))
    ax.text(4.0, yy + 2.0, f"{v:.1f}% {lab}".replace('.', ',') if pt else f"{v:.1f}% {lab}", fontsize=9.6, color=INK, va='bottom')
# ---------------- Panel 2: data
panel(31, 40, 27, 32, '2', T('Dados de poços', 'Well data'), BLUE)
# well icon
ax.add_patch(Rectangle((35.0, 46.5), 8, 12.5, fc='#e9edf2', ec='#7b8794', lw=1.6))
ax.add_patch(Rectangle((35.0, 46.5), 8, 5.2, fc='#8ec1f0', ec='none'))
ax.add_patch(Ellipse((39, 59), 8, 1.8, fc='#d7dde4', ec='#7b8794', lw=1.6))
ax.plot([39, 39], [59, 64.2], color='#7b8794', lw=2.2); ax.plot([39, 45.2], [64.2, 64.2], color='#7b8794', lw=2.2); ax.plot([45.2, 45.2], [64.2, 61.4], color='#7b8794', lw=2.2)
ax.add_patch(Polygon([[45.2, 61.0], [44.3, 59.4], [46.1, 59.4]], fc=BLUE, ec='none')); ax.add_patch(Circle((45.2, 59.0), 0.92, fc=BLUE, ec='none'))
ax.text(52.5, 61.5, '165', fontsize=20, fontweight='bold', color=BLUE, ha='center')
ax.text(52.5, 58.4, T('poços (2018)', 'wells (2018)'), fontsize=10.5, color=MUT, ha='center')
ax.text(52.5, 54.6, T('23 parâmetros', '23 parameters'), fontsize=10.5, color=INK, ha='center')
for j, (lab, c) in enumerate([(T('Físico-\nquímico', 'Physico-\nchemical'), AQ), (T('Microbio-\nlógico', 'Microbio-\nlogical'), BLUE), (T('Metais pesados', 'Heavy metals'), YEL)]):
    ax.add_patch(FancyBboxPatch((34.0 + j * 7.9, 42.1), 7.3, 3.2, boxstyle='round,pad=0.15,rounding_size=0.9', fc=c, ec='none'))
    ax.text(34.0 + j * 7.9 + 3.65, 43.7, lab.replace(' ', '\n').replace('-q', '-\nq') if False else lab.replace(' ', '\n'), fontsize=7.0, linespacing=0.95, color='white', ha='center', va='center', fontweight='bold')
# ---------------- Panel 3: excursion curve
panel(61, 40, 27, 32, '3', T('Excursão sem saturação', 'Unbounded excursion'), BLUE)
x0, y0, W, H = 66, 45.0, 19, 19
ax.plot([x0, x0 + W], [y0, y0], color=MUT, lw=1.2); ax.plot([x0, x0], [y0, y0 + H], color=MUT, lw=1.2)
r = np.linspace(1, 12, 200); xx = 100 * (1 - 1 / r)
X = x0 + (r - 1) / 11 * W; Y = y0 + xx / 100 * H
ax.plot([x0 - 1.8, x0], [y0, y0], color=AQ, lw=3); ax.plot(X, Y, color=BLUE, lw=3)
sq = np.minimum(100, (r - 1) ** 2 * 100); ax.plot(X, y0 + sq / 100 * H, color=GRY, lw=1.6, ls='--')
for rv, lab in [(2, '50'), (10, '90')]:
    xv = x0 + (rv - 1) / 11 * W; yv = y0 + 100 * (1 - 1 / rv) / 100 * H
    ax.add_patch(Circle((xv, yv), 0.55, fc=BLUE, ec='white', lw=1)); ax.text(xv + 0.6, yv - 2.0, lab, fontsize=9.5, color=BLUE, fontweight='bold')
ax.text(x0 + W, y0 - 2.4, T('v / VMP', 'v / MAV'), fontsize=9.5, color=MUT, ha='right')
ax.text(x0 - 1.0, y0 + H + 0.6, 'x', fontsize=11, color=MUT, ha='center', style='italic')
ax.text(x0 + W, y0 + H + 1.0, T('quadrática (v12) satura', 'quadratic (v12) saturates'), fontsize=8.2, color=GRY, ha='right', va='bottom')
# ---------------- Panel 4: weighting & GP
panel(91, 40, 28, 32, '4', T('Pesos por cenário', 'Scenario weights'), BLUE)
lens = [(T('Saúde', 'Health'), ORA), (T('Saneam.', 'Sanit.'), AQ), (T('Tratab.', 'Treat.'), VIO), (T('Conform.', 'Compl.'), GRY)]
cx = [95.2, 101.0, 106.8, 112.6]
for (lab, c), x in zip(lens, cx):
    ax.add_patch(Circle((x, 63.0), 2.5, fc=c, ec='none'))
    ax.text(x, 59.4, lab, fontsize=8.6, color=INK, ha='center')
# icons inside lens circles
ax.text(cx[0], 63.0, '♥', fontsize=15, color='white', ha='center', va='center')
ax.add_patch(Polygon([[cx[1], 64.9], [cx[1] - 1.2, 62.7], [cx[1] + 1.2, 62.7]], fc='white', ec='none')); ax.add_patch(Circle((cx[1], 62.4), 1.25, fc='white', ec='none'))
for a in range(0, 360, 45):
    t = np.radians(a); ax.add_patch(Rectangle((cx[2] + 1.15 * np.cos(t) - 0.35, 63 + 1.15 * np.sin(t) - 0.35), 0.7, 0.7, angle=0, fc='white', ec='none'))
ax.add_patch(Circle((cx[2], 63.0), 1.15, fc='white', ec='none')); ax.add_patch(Circle((cx[2], 63.0), 0.5, fc=VIO, ec='none'))
ax.plot([cx[3] - 1.5, cx[3] + 1.5], [63.9, 63.9], color='white', lw=1.8); ax.plot([cx[3], cx[3]], [61.6, 64.6], color='white', lw=1.8)
ax.add_patch(Wedge((cx[3] - 1.5, 63.3), 0.8, 180, 360, fc='white')); ax.add_patch(Wedge((cx[3] + 1.5, 63.3), 0.8, 180, 360, fc='white'))
# CRITIC data
ax.add_patch(FancyBboxPatch((94.6, 51.8), 7.2, 4.4, boxstyle='round,pad=0.2,rounding_size=0.8', fc='white', ec=BLUE, lw=1.6))
for k, hgt in enumerate([1.2, 2.4, 1.6, 3.0]): ax.add_patch(Rectangle((95.9 + k * 1.3, 52.5), 0.8, hgt, fc=BLUE, ec='none'))
ax.text(98.2, 50.3, 'CRITIC', fontsize=8.5, color=BLUE, ha='center', va='center', fontweight='bold')
# target
for rr, c in [(4.1, '#f2d2c3'), (2.9, '#ffffff'), (1.8, ORA), (0.8, 'white')]: ax.add_patch(Circle((111.5, 49.6), rr, fc=c, ec=ORA if c == '#ffffff' else 'none', lw=1))
arrow((102.2, 53.5), (107.2, 51.0), col=BLUE, lw=1.8); arrow((111.5, 58.4), (111.5, 54.2), col=GRY, lw=1.8)
ax.text(111.5, 42.6, T('compromisso\ndados × visão', 'data × lens\ncompromise'), fontsize=8.6, color=INK, ha='center', va='bottom')
ax.text(98.2, 46.0, T('+ restrições\nnormativas', '+ normative\nconstraints'), fontsize=8.6, color=MUT, ha='center', va='center')
# arrows between top panels
for xa in [28.4, 58.4, 88.4]: arrow((xa, 56), (xa + 2.4, 56))
arrow((105, 39.6), (105, 35.0))
# ---------------- Panel 5: additive aggregation
panel(66, 3, 53, 31, '5', T('Agregação aditiva + cobertura', 'Additive aggregation + coverage'), BLUE)
bx, by = 70, 14.5
segs = [(AQ, 7.5, T('FQ', 'PC')), (BLUE, 11, 'MB'), (YEL, 6.5, T('MP', 'HM'))]
cur = bx
for c, w, lab in segs:
    ax.add_patch(Rectangle((cur, by), w, 5.2, fc=c, ec='white', lw=2)); ax.text(cur + w / 2, by + 2.6, lab, color='white', fontsize=11, fontweight='bold', ha='center', va='center'); cur += w
ax.add_patch(Rectangle((cur, by), 5.5, 5.2, fc='none', ec=GRY, lw=1.6, ls=(0, (3, 2))))
ax.text(cur + 2.75, by + 2.6, '?', color=GRY, fontsize=14, ha='center', va='center', fontweight='bold')
ax.text(bx, by + 9.0, 'IPA = Σ wᵢ·xᵢ  (= 0 ⇔ ' + T('conforme', 'compliant') + ')', fontsize=13, color=INK)
ax.text(cur + 6.5, by + 3.4, T('parâmetro\nfaltante', 'missing\nparameter'), fontsize=9.6, color=MUT, va='center')
ax.text(bx, by - 3.4, T('Faltante → IPA é limite inferior, com cobertura C = Σw medidos / Σw', 'Missing → IPA is a lower bound, with coverage C = Σw measured / Σw'), fontsize=9.6, color=MUT)
ax.text(bx, 6.0, T('Multiplicativo (IQA): falta 1 parâmetro → índice indefinido', 'Multiplicative (WQI): 1 missing parameter → index undefined'), fontsize=9.6, color='#a8431d')
arrow((65.6, 18), (61.6, 18))
# ---------------- Panel 6: severity scale with interventions
panel(1, 3, 60, 31, '6', T('Gravidade da não potabilidade → intervenção', 'Severity of non-potability → intervention'), ORA)
labs = [T('Potável', 'Potable'), T('Não potável\nN1', 'Non-potable\nL1'), T('Não potável\nN2', 'Non-potable\nL2'), T('Não potável\nN3', 'Non-potable\nL3'), T('Não potável\nN4', 'Non-potable\nL4')]
rng = ['IPA = 0', '0–75', '75–150', T('150–225\nou veto', '150–225\nor veto'), '> 225']
act = [T('vigilância', 'surveillance'), T('correção\nsimples', 'simple\ncorrection'), T('tratamento\nconvencional', 'conventional\ntreatment'), T('tratamento\navançado', 'advanced\ntreatment'), T('fonte\nalternativa', 'alternative\nsource')]
for i in range(5):
    x = 3.2 + i * 11.4
    ax.add_patch(FancyBboxPatch((x, 17.4), 10.6, 8.0, boxstyle='round,pad=0.15,rounding_size=0.8', fc=SEV[i], ec='white', lw=2))
    ax.text(x + 5.3, 22.6, labs[i], fontsize=8.8, color='white', ha='center', va='center', fontweight='bold', linespacing=1.05)
    ax.text(x + 5.3, 18.9, rng[i], fontsize=7.8, color='white', ha='center', va='center', linespacing=1.0)
    # icon
    ic = (x + 5.3, 12.9)
    if i == 0:
        ax.add_patch(Circle(ic, 1.9, fc='white', ec=SEV[0], lw=2)); ax.plot([ic[0] - 0.9, ic[0] - 0.2, ic[0] + 1.0], [ic[1], ic[1] - 0.8, ic[1] + 0.9], color=SEV[0], lw=2.4)
    elif i == 1:
        ax.add_patch(Polygon([[ic[0], ic[1] + 2.2], [ic[0] - 1.3, ic[1] - 0.1], [ic[0] + 1.3, ic[1] - 0.1]], fc=SEV[1], ec='none')); ax.add_patch(Circle((ic[0], ic[1] - 0.4), 1.33, fc=SEV[1], ec='none'))
    elif i == 2:
        ax.add_patch(Rectangle((ic[0] - 2.0, ic[1] - 1.6), 4.0, 2.4, fc=SEV[2], ec='none')); ax.add_patch(Polygon([[ic[0] - 2.2, ic[1] + 0.8], [ic[0], ic[1] + 2.2], [ic[0] + 2.2, ic[1] + 0.8]], fc=SEV[2]))
        ax.add_patch(Rectangle((ic[0] - 0.5, ic[1] - 1.6), 1.0, 1.4, fc='white', ec='none'))
    elif i == 3:
        ax.add_patch(Polygon([[ic[0], ic[1] + 2.0], [ic[0] - 2.1, ic[1] - 1.6], [ic[0] + 2.1, ic[1] - 1.6]], fc=SEV[3])); ax.text(ic[0], ic[1] - 0.4, '!', color='white', fontsize=13, ha='center', va='center', fontweight='bold')
    else:
        ax.add_patch(Rectangle((ic[0] - 2.4, ic[1] - 1.0), 3.2, 2.2, fc=SEV[4])); ax.add_patch(Rectangle((ic[0] + 0.8, ic[1] - 1.0), 1.6, 1.5, fc=SEV[4]))
        for wx in [ic[0] - 1.6, ic[0] + 1.4]: ax.add_patch(Circle((wx, ic[1] - 1.3), 0.55, fc='white', ec=SEV[4], lw=1.4))
    ax.text(x + 5.3, 8.2, act[i], fontsize=8.4, color=INK, ha='center', va='center', linespacing=1.05)
ax.add_patch(FancyArrowPatch((3.5, 27.4), (59.0, 27.4), arrowstyle='-|>', mutation_scale=16, color=SEV[4], lw=2))
ax.text(31, 28.4, T('gravidade crescente', 'increasing severity'), fontsize=9.4, color=SEV[4], ha='center', va='bottom')
ax.text(31, 4.6, T('Robustez: Monte Carlo e Sobol · varredura de λ · parâmetros faltantes · IQA/CCME', 'Robustness: Monte Carlo and Sobol · λ sweep · missing parameters · WQI/CCME'), fontsize=9.0, color=MUT, ha='center')
fig.savefig(f'figs/{lang}_f1_infografico.png', dpi=400, facecolor=BG); print('ok')
