import openpyxl, numpy as np, pandas as pd
def load(path):
    wb=openpyxl.load_workbook(path,data_only=True); ws=wb.active
    rows=list(ws.iter_rows(values_only=True))
    cols=['amonia','nitrito','nitrato','dureza','cloreto','cor','pH','SDT','sulfato','turbidez','ct','ec','al','ba','cd','pb','cu','cr','fe','mn','ni','na','zn']
    df=pd.DataFrame(rows[1:],columns=cols)
    for c in ['ct','ec']:
        df[c]=df[c].astype(str).str.strip().str.lower().map(lambda s: 1 if s.startswith('pres') else (0 if s.startswith('aus') else np.nan))
    for c in cols:
        if c not in ('ct','ec'): df[c]=pd.to_numeric(df[c],errors='coerce')
    return df
VMP={'amonia':1.2,'nitrito':1.0,'nitrato':10.0,'dureza':300,'cloreto':250,'cor':15,'SDT':500,'sulfato':250,'turbidez':5.0,
 'al':0.2,'ba':0.7,'cd':0.003,'pb':0.01,'cu':2.0,'cr':0.05,'fe':0.3,'mn':0.1,'ni':0.07,'na':200,'zn':5.0}
W={'pH':0.4,'turbidez':0.7,'cor':0.6,'cloreto':0.3,'sulfato':0.3,'al':0.9,'amonia':0.8,'nitrito':0.85,'nitrato':0.75,'SDT':0.4,
 'dureza':0.4,'fe':0.5,'mn':0.6,'zn':0.4,'na':0.5,'cu':0.7,'cr':0.8,'ni':0.8,'cd':1.0,'pb':1.0,'ba':0.7,'ct':0.9,'ec':1.0}
def classify(v):
    if v==0: return 'Potável'
    if v<=75: return 'Nível 1'
    if v<=150: return 'Nível 2'
    if v<=225: return 'Nível 3'
    return 'Nível 4'
ORDER=['Potável','Nível 1','Nível 2','Nível 3','Nível 4']
