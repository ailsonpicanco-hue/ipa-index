import sys, json; sys.path.insert(0,'scripts')
from load import *
from scipy.optimize import linprog
from scipy.stats import spearmanr
rng=np.random.default_rng(2026)
df=pd.read_pickle('data/v12.pkl')
P=['amonia','nitrito','nitrato','dureza','cloreto','cor','pH','SDT','sulfato','turbidez','ct','ec','al','ba','cd','pb','cu','cr','fe','mn','ni','na','zn']
ANEXO9=['nitrato','nitrito','ba','cd','pb','cu','cr','ni']
CHEM=[p for p in P if p not in ('ct','ec')]
def XN(d):
    X=pd.DataFrame(index=d.index); p=d.pH; e=np.where(p<6,6-p,np.where(p>9,p-9,0)); X['pH']=100*e/(1+e)
    for k,v in VMP.items(): e=np.where(d[k]>v,d[k]/v-1,0); X[k]=100*e/(1+e)
    X['ct']=d.ct*100; X['ec']=d.ec*100; return X[P]
X=XN(df)
viol=pd.DataFrame({k:df[k]>v for k,v in VMP.items()}); viol['pH']=(df.pH<6)|(df.pH>9); viol['ct']=df.ct==1; viol['ec']=df.ec==1
veto=viol.ec|viol[ANEXO9].any(axis=1)
# ---- lens tiers (1.0 / 0.6 / 0.2)
LENS={
 'Saude':{1.0:['ec']+ANEXO9, 0.6:['ct','al','mn','amonia','turbidez'], 0.2:['dureza','cloreto','sulfato','SDT','cor','fe','na','zn','pH']},
 'Saneamento':{1.0:['ec','ct','amonia','nitrato','nitrito'], 0.6:['turbidez','cloreto','cor','SDT'], 0.2:['al','ba','cd','pb','cu','cr','fe','mn','ni','na','zn','dureza','sulfato','pH']},
 'Tratabilidade':{1.0:['pb','cd','cr','ni','ba','cu','nitrato','nitrito','SDT','cloreto','na','dureza','sulfato','zn'], 0.6:['fe','mn','al','turbidez','cor','amonia','ec'], 0.2:['pH','ct']},
 'Conformidade':{1.0:P},
}
for L,t in LENS.items():
    allp=sum(t.values(),[]); assert sorted(allp)==sorted(P),(L,set(P)^set(allp))
WL={L:pd.Series({p:w for w,ps in t.items() for p in ps})[P] for L,t in LENS.items()}
WL['Especialistas']=pd.Series(W)[P]
# ---- unsupervised CRITIC and entropy on excursion matrix
def critic(X):
    Z=(X-X.min())/(X.max()-X.min()).replace(0,np.nan); Z=Z.fillna(0); s=Z.std(); R=Z.corr().fillna(0)
    c=s*(1-R).sum(); return c/c.sum()
def entropy(X):
    Y=X+1e-9; Pm=Y/Y.sum(); E=-(Pm*np.log(Pm)).sum()/np.log(len(X)); d=1-E; d[X.max()==0]=0; return d/d.sum()
wc=critic(X); we=entropy(X)
# ---- GP: data-informed lens weights. target = lam*lens + (1-lam)*critic (rescaled to lens total); hard constraints: tier order, E. coli >= any chemical (health & sanitation), sum preserved
def gp_lens(L, lam=0.7, lo=0.05, hi=1.5):
    wl=WL[L]; tot=wl.sum(); wcs=wc*tot; target=lam*wl+(1-lam)*wcs
    n=len(P); nv=3*n  # w, d+, d-
    c=np.r_[np.zeros(n),np.ones(2*n)]
    Aeq=[];beq=[]
    for i in range(n):
        r=np.zeros(nv); r[i]=1; r[n+i]=-1; r[2*n+i]=1; Aeq.append(r); beq.append(target.iloc[i])  # w - d+ + d- = target
    r=np.zeros(nv); r[:n]=1; Aeq.append(r); beq.append(tot)
    Aub=[];bub=[]
    tiers=sorted(LENS.get(L,{}).items(),key=lambda kv:-kv[0])
    for a in range(len(tiers)-1):
        for i in tiers[a][1]:
            for j in tiers[a+1][1]:
                r=np.zeros(nv); r[P.index(j)]=1; r[P.index(i)]=-1; Aub.append(r); bub.append(-0.1)
    if L in ('Saude','Saneamento','Especialistas'):
        for j in CHEM:
            r=np.zeros(nv); r[P.index(j)]=1; r[P.index('ec')]=-1; Aub.append(r); bub.append(0)
    res=linprog(c,A_ub=np.array(Aub) if Aub else None,b_ub=np.array(bub) if bub else None,A_eq=np.array(Aeq),b_eq=np.array(beq),bounds=[(lo,hi)]*n+[(0,None)]*(2*n),method='highs')
    assert res.status==0,(L,res.message)
    return pd.Series(res.x[:n],index=P), float(res.fun), target
WF={};GPd={}
for L in ['Especialistas','Saude','Saneamento','Tratabilidade','Conformidade']:
    w,f,tg=gp_lens(L); WF[L]=w; GPd[L]={'total_abs_deviation_from_target':round(f,3),'weights_changed_vs_lens':int((np.abs(w-WL[L])>0.05).sum())}
WF['CRITIC_puro']=wc*WL['Conformidade'].sum(); WF['Entropia_pura']=we*WL['Conformidade'].sum()
def cls_vec(s):
    return pd.Series(np.select([s==0,s<=75,s<=150,s<=225],['Potável','Nível 1','Nível 2','Nível 3'],'Nível 4'),index=s.index)
def two(s):
    c=cls_vec(s); c[veto & c.isin(['Potável','Nível 1','Nível 2'])]='Nível 3'; return c
IPA=pd.DataFrame({L:(X*w).sum(axis=1) for L,w in WF.items()})
CL=pd.DataFrame({L:two(IPA[L]) for L in WF})
O={}
O['weights']=pd.DataFrame(WF).round(3).to_dict()
O['weights_lens_raw']=pd.DataFrame(WL).round(2).to_dict()
O['critic']=wc.round(4).to_dict(); O['entropy']=we.round(4).to_dict()
O['GP']=GPd
O['counts']={L:CL[L].value_counts().reindex(ORDER).fillna(0).astype(int).to_dict() for L in CL}
sc=list(WF)
O['spearman']=pd.DataFrame({a:{b:round(spearmanr(IPA[a],IPA[b]).statistic,2) for b in sc} for a in sc}).to_dict()
O['class_change_vs_especialistas']={L:int((CL[L]!=CL['Especialistas']).sum()) for L in CL}
pol=['Especialistas','Saude','Saneamento','Tratabilidade','Conformidade']
top={L:set(IPA[L].nlargest(20).index) for L in pol}; rob=set.intersection(*top.values())
O['robust_top20']=sorted(int(i)+1 for i in rob)
# group shares (health lens and experts)
GR={'Físico-químico':['amonia','nitrito','nitrato','dureza','cloreto','cor','SDT','sulfato','turbidez','pH','na'],'Microbiológico':['ct','ec'],'Metais':['al','ba','cd','pb','cu','cr','fe','mn','ni','zn']}
O['group_share']={L:{g:round(100*(X[c]*WF[L][c]).sum().sum()/(X*WF[L]).sum().sum(),1) for g,c in GR.items()} for L in pol}
# SMAA around each lens final weights (+/-30%)
sm={}
for L in pol:
    base=WF[L].values; acc=np.zeros((len(df),5))
    for _ in range(3000):
        w=base*rng.uniform(0.7,1.3,len(base)); s=X.values@w
        c=np.select([s==0,s<=75,s<=150,s<=225],[0,1,2,3],4); c=np.where(veto.values&(c<3),3,c); acc[np.arange(len(df)),c]+=1
    acc/=3000; sm[L]={'stable95':int((acc.max(1)>=0.95).sum()),'ambig70':int((acc.max(1)<0.7).sum())}
O['smaa_pm30']=sm
# Jenks natural breaks on Especialistas IPA>0 (k=4)
def jenks(v,k):
    v=np.sort(v); n=len(v); mat1=np.zeros((n+1,k+1)); mat2=np.full((n+1,k+1),np.inf)
    for j in range(1,k+1): mat1[1,j]=1; mat2[1,j]=0
    for l in range(2,n+1):
        s1=s2=w=0
        for m in range(1,l+1):
            i3=l-m+1; val=v[i3-1]; s2+=val*val; s1+=val; w+=1; var=s2-s1*s1/w; i4=i3-1
            if i4!=0:
                for j in range(2,k+1):
                    if mat2[l,j]>=var+mat2[i4,j-1]: mat1[l,j]=i3; mat2[l,j]=var+mat2[i4,j-1]
        mat1[l,1]=1; mat2[l,1]=var
    br=[v[-1]]; kk=n
    for j in range(k,1,-1): idx=int(mat1[kk,j])-2; br.append(v[idx]); kk=int(mat1[kk,j])-1
    return sorted(br)
for L in ['Especialistas','Saude']:
    v=IPA[L][IPA[L]>0].values; O[f'jenks_{L}']=[round(b,1) for b in jenks(v,4)]
# missing groups (health lens)
def subset(keep,L='Saude'):
    w=WF[L]; s=(X[keep]*w[keep]).sum(axis=1); c=cls_vec(s)
    vt=viol['ec'] if 'ec' in keep else pd.Series(False,index=df.index)
    a9=[p for p in ANEXO9 if p in keep]
    if a9: vt=vt|viol[a9].any(axis=1)
    c[vt & c.isin(['Potável','Nível 1','Nível 2'])]='Nível 3'
    cov=w[keep].sum()/(w.sum()+1.0)
    full=CL[L]; nc=full!='Potável'
    return {'n_param':len(keep),'cobertura_pct':round(100*cov,1),'classe_igual_pct':round(100*(c==full).mean(),1),
            'nao_conformes_detectados_pct':round(100*((c!='Potável')&nc).sum()/nc.sum(),1),'potavel_aparente':int((c=='Potável').sum())}
cases={'Completo':P,'Sem metais':GR['Físico-químico']+GR['Microbiológico'],'Microbiologia + pH + turbidez + cor':['ct','ec','pH','turbidez','cor'],'Sem microbiologia':GR['Físico-químico']+GR['Metais'],'Só metais':GR['Metais']}
O['missing']={k:subset(v) for k,v in cases.items()}
O['veto']={'total':int(veto.sum()),'ec':int(viol.ec.sum()),'anexo9_only':int((viol[ANEXO9].any(axis=1)&~viol.ec).sum())}
json.dump(O,open('data/final.json','w'),ensure_ascii=False,indent=1)
IPA.to_pickle('data/final_ipa.pkl'); CL.to_pickle('data/final_cl.pkl'); pd.DataFrame(WF).to_csv('data/final_weights.csv')
print(json.dumps({k:O[k] for k in ['GP','counts','class_change_vs_especialistas','robust_top20','group_share','smaa_pm30','jenks_Especialistas','jenks_Saude','missing','veto']},ensure_ascii=False,indent=1))
print(pd.DataFrame(WF).round(2).to_string())
print('spearman policy:',{a:{b:O['spearman'][a][b] for b in pol} for a in pol})
