import sys; sys.path.insert(0,"scripts"); from bump import bump; import json, numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'scripts'); from load import VMP
lang=sys.argv[1]; pt=lang=='pt'
NAVY='#0d366b'; BLUE='#2a78d6'; OR='#eb6834'; AQ='#1baf7a'; INK='#0b0b0b'; MUT='#52514e'; BG='white'
ORD=['#1baf7a','#f0915f','#d9602f','#a8431d','#6e2a10']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9.5,'figure.facecolor':BG,'axes.facecolor':BG,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#8a8984','xtick.color':MUT,'ytick.color':MUT,'axes.labelcolor':MUT})
O=json.load(open('data/final.json')); df=pd.read_pickle('data/v12.pkl'); IPA=pd.read_pickle('data/final_ipa.pkl'); W=pd.read_csv('data/final_weights.csv',index_col=0)
CLS=['Potável','Nível 1','Nível 2','Nível 3','Nível 4']
CLL=CLS if pt else ['Potable','Non-potable L1','Non-potable L2','Non-potable L3','Non-potable L4']
if pt: CLL=['Potável','Não potável N1','Não potável N2','Não potável N3','Não potável N4']
LN={'Especialistas':('Especialistas (referência)','Experts (baseline)'),'Saude':('Saúde pública','Public health'),'Saneamento':('Saneamento','Sanitation'),'Tratabilidade':('Tratabilidade','Treatability'),
    'Conformidade':('Conformidade legal','Legal compliance'),'CRITIC_puro':('CRITIC puro (dados)','CRITIC only (data)'),'Entropia_pura':('Entropia pura (dados)','Entropy only (data)')}
L=lambda k: LN[k][0 if pt else 1]
num2=lambda v,d=2: (f'{v:.{d}f}'.replace('.',',') if pt else f'{v:.{d}f}')
GR={'amonia':'PC','nitrito':'PC','nitrato':'PC','dureza':'PC','cloreto':'PC','cor':'PC','SDT':'PC','sulfato':'PC','turbidez':'PC','pH':'PC','na':'PC','ct':'MB','ec':'MB','al':'HM','ba':'HM','cd':'HM','pb':'HM','cu':'HM','cr':'HM','fe':'HM','mn':'HM','ni':'HM','zn':'HM'}
GC={'PC':AQ,'MB':BLUE,'HM':'#eda100'}; GL={'PC':('Físico-químico','Physicochemical'),'MB':('Microbiológico','Microbiological'),'HM':('Metais pesados','Heavy metals')}
PN={'amonia':('Amônia','Ammonia'),'nitrito':('Nitrito','Nitrite'),'nitrato':('Nitrato','Nitrate'),'dureza':('Dureza','Hardness'),'cloreto':('Cloreto','Chloride'),'cor':('Cor aparente','Apparent colour'),'SDT':('SDT','TDS'),'sulfato':('Sulfato','Sulphate'),'turbidez':('Turbidez','Turbidity'),'pH':('pH','pH'),'na':('Na','Na'),'ct':('Coliformes totais','Total coliforms'),'ec':('E. coli','E. coli'),'al':('Al','Al'),'ba':('Ba','Ba'),'cd':('Cd','Cd'),'pb':('Pb','Pb'),'cu':('Cu','Cu'),'cr':('Cr','Cr'),'fe':('Fe','Fe'),'mn':('Mn','Mn'),'ni':('Ni','Ni'),'zn':('Zn','Zn')}
# R1 exceedance prevalence
viol={k:(df[k]>v).mean()*100 for k,v in VMP.items()}; viol['pH']=((df.pH<6)|(df.pH>9)).mean()*100; viol['ct']=df.ct.mean()*100; viol['ec']=df.ec.mean()*100
s=pd.Series(viol).sort_values()
fig,ax=plt.subplots(figsize=(8,6))
ax.barh([PN[k][0 if pt else 1] for k in s.index],s.values,color=[GC[GR[k]] for k in s.index],height=0.65)
for i,v in enumerate(s.values): ax.text(v+0.6,i,(f'{v:.1f}%'.replace('.',',') if pt else f'{v:.1f}%'),va='center',fontsize=8,color=INK)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=GC[g],label=GL[g][0 if pt else 1]) for g in ['MB','PC','HM']],frameon=False,loc='lower right')
ax.set_xlabel('% de amostras fora do padrão\n(VMP; pH fora de 6,0–9,0; Portaria GM/MS 888/2021)' if pt else '% of samples outside the standard\n(MAV; pH outside 6.0–9.0; Ordinance GM/MS 888/2021)')
ax.set_title(('Frequência de violação por parâmetro (n = 165)' if pt else 'Exceedance frequency by parameter (n = 165)'),loc='left',color=INK,fontsize=11)
bump(fig,1.15); fig.tight_layout() if not getattr(fig,'_notight',False) else None; fig.savefig(f'figs/{lang}_s1_violacoes.png',dpi=400); plt.close()
# R2+R3 combined: (a) classes by lens (b) components
sc=['Especialistas','Saude','Saneamento','Tratabilidade','Conformidade','CRITIC_puro','Entropia_pura']
fig,(ax,ax2)=plt.subplots(1,2,figsize=(15,8.8),gridspec_kw={'width_ratios':[1,1.15],'wspace':0.25}); left=np.zeros(len(sc))
for i,k in enumerate(CLS):
    v=np.array([O['counts'][s_][k] for s_ in sc]); ax.barh(range(len(sc)),v,left=left,color=ORD[i],edgecolor=BG,linewidth=2,label=CLL[i])
    for j,(l,val) in enumerate(zip(left,v)):
        if val>=8: ax.text(l+val/2,j,str(val),ha='center',va='center',fontsize=8,color=INK if i==1 else 'white',fontweight='bold')
    left+=v
ax.set_yticks(range(len(sc)),[L(s_) for s_ in sc]); ax.invert_yaxis(); ax.set_xlabel('Nº de amostras' if pt else 'No. of samples'); ax.set_xlim(0,165)
ax.legend(ncol=3,frameon=False,bbox_to_anchor=(-0.02,1.0),loc='lower left',fontsize=7.6,handlelength=1.2,columnspacing=0.9)
ax.axhline(4.5,color=MUT,lw=0.8,ls=':')
ax.set_title('(a) '+('Classes por cenário de ponderação' if pt else 'Classes by weighting lens'),loc='left',color=INK,fontsize=10.5,pad=48)
P=list(W.index)
def XN(d):
    X=pd.DataFrame(index=d.index); p=d.pH; e=np.where(p<6,6-p,np.where(p>9,p-9,0)); X['pH']=100*e/(1+e)
    for k,v in VMP.items(): e=np.where(d[k]>v,d[k]/v-1,0); X[k]=100*e/(1+e)
    X['ct']=d.ct*100; X['ec']=d.ec*100; return X[P]
X=XN(df); w=W['Saude']; C=pd.DataFrame({g:(X[[p for p in P if GR[p]==g]]*w[[p for p in P if GR[p]==g]]).sum(axis=1) for g in ['MB','HM','PC']})
C=C.loc[C.sum(axis=1).sort_values(ascending=False).index]
bot=np.zeros(len(C)); xx=np.arange(len(C))
for g in ['MB','HM','PC']: ax2.bar(xx,C[g],bottom=bot,color=GC[g],width=0.9,edgecolor='white',linewidth=0.25,label=GL[g][0 if pt else 1]); bot+=C[g].values
for t,lb in [(75,'N1 | N2' if pt else 'L1 | L2'),(150,'N2 | N3' if pt else 'L2 | L3'),(225,'N3 | N4' if pt else 'L3 | L4')]:
    ax2.axhline(t,color='#8a8984',lw=0.8,ls='--'); ax2.text(len(C)-1,t+4,lb,ha='right',fontsize=8,color=MUT)
ax2.set_xticks([]); ax2.set_ylabel('IPA (cenário Saúde pública)' if pt else 'IPA (public-health lens)')
ax2.set_xlabel(('Amostras ordenadas pelo IPA\n(as 22 potáveis, IPA = 0, ficam à direita)' if pt else 'Samples ranked by IPA\n(the 22 potable samples, IPA = 0, are on the right)'))
ax2.legend(frameon=False,ncol=3,loc='upper right')
ax2.set_title('(b) '+('Contribuição dos componentes por amostra' if pt else 'Component contribution per sample'),loc='left',color=INK,fontsize=10.5,pad=48)
bump(fig,1.15); fig.subplots_adjust(left=0.155,right=0.99,top=0.86,bottom=0.12); fig.savefig(f'figs/{lang}_f5_resultados.png',dpi=400); plt.close()
# R4 missing groups
M=O['missing']; names={'Completo':('Completo (23 parâmetros)','Complete (23 parameters)'),'Sem metais':('Sem metais','Without metals'),'Microbiologia + pH + turbidez + cor':('Micro + pH + turbidez + cor','Micro + pH + turbidity + colour'),'Sem microbiologia':('Sem microbiologia','Without microbiology'),'Só metais':('Só metais','Metals only')}
fig,ax=plt.subplots(figsize=(8.5,4)); y=np.arange(len(M)); h=0.36; ks=list(M)
a=[M[k]['nao_conformes_detectados_pct'] for k in ks]; b=[M[k]['classe_igual_pct'] for k in ks]
ax.barh(y-h/2-0.01,a,h,color=BLUE,label='Amostras não potáveis detectadas (%)' if pt else 'Non-potable samples detected (%)')
ax.barh(y+h/2+0.01,b,h,color=OR,label='Mesma classe do caso completo (%)' if pt else 'Same class as complete case (%)')
for i in range(len(ks)): ax.text(a[i]+1,y[i]-h/2,f'{a[i]:.0f}',va='center',fontsize=8,color=INK); ax.text(b[i]+1,y[i]+h/2,f'{b[i]:.0f}',va='center',fontsize=8,color=INK)
ax.set_yticks(y,[f"{names[k][0 if pt else 1]}\n({'cobertura' if pt else 'coverage'} {M[k]['cobertura_pct']:.0f}%)" for k in ks],fontsize=8.5); ax.invert_yaxis(); ax.set_xlim(0,112)
ax.legend(frameon=False,bbox_to_anchor=(0,1.0),loc='lower left',ncol=2,fontsize=8.5)
bump(fig,1.15); fig.tight_layout() if not getattr(fig,'_notight',False) else None; fig.savefig(f'figs/{lang}_f7_faltantes.png',dpi=400); plt.close()
# R5 robustness: spearman + lambda sweep + sobol + probability of severe class
SE=json.load(open('data/sensitivity.json'))
pol=['Especialistas','Saude','Saneamento','Tratabilidade','Conformidade']
LC={'Especialistas':'#8a8984','Saude':OR,'Saneamento':AQ,'Tratabilidade':'#6250d6','Conformidade':BLUE}
R=pd.DataFrame(O['spearman']).loc[pol,pol]
fig,axs=plt.subplots(2,2,figsize=(13,9.6),gridspec_kw={'hspace':0.5,'wspace':0.38}); a1,a2,a3,a4=axs.ravel()
from matplotlib.colors import LinearSegmentedColormap
cm=LinearSegmentedColormap.from_list('b',['#cde2fb','#86b6ef','#3987e5','#1c5cab','#0d366b'])
a1.imshow(R.values,cmap=cm,vmin=0.85,vmax=1)
for i_ in range(len(pol)):
    for j_ in range(len(pol)): a1.text(j_,i_,num2(R.values[i_,j_]),ha='center',va='center',fontsize=8.5,color='white' if R.values[i_,j_]>0.95 else INK)
a1.set_xticks(range(len(pol)),[L(p_).split(' (')[0] for p_ in pol],rotation=30,ha='right',fontsize=8); a1.set_yticks(range(len(pol)),[L(p_).split(' (')[0] for p_ in pol],fontsize=8)
for s_ in a1.spines.values(): s_.set_visible(False)
a1.set_title('(a) '+('ρ de Spearman entre cenários' if pt else 'Spearman ρ between lenses'),loc='left',color=INK,fontsize=10.5)
for Lk in pol:
    r=SE['lambda_sweep'][Lk]; a2.plot([x['lam'] for x in r],[x['same_class_pct'] for x in r],color=LC[Lk],lw=2,marker='o',ms=3.5,label=L(Lk).split(' (')[0])
a2.axvline(0.7,color=MUT,ls='--',lw=0.9); a2.axhline(90,color='#b4b2ab',ls=':',lw=0.9)
a2.text(0.71,a2.get_ylim()[0] if False else 62,'λ = 0,7' if pt else 'λ = 0.7',fontsize=8,color=MUT)
a2.set_xlabel('λ (0 = '+('só dados' if pt else 'data only')+'; 1 = '+('só visão' if pt else 'lens only')+')'); a2.set_ylabel('% '+('mesma classe que λ = 0,7' if pt else 'same class as λ = 0.7'))
a2.set_ylim(60,102); a2.legend(frameon=False,fontsize=7.5,loc='lower left',ncol=2)
a2.set_title('(b) '+('Sensibilidade ao parâmetro λ da PM' if pt else 'Sensitivity to the GP parameter λ'),loc='left',color=INK,fontsize=10.5)
ST=pd.Series(SE['sobol']['ST']); S1=pd.Series(SE['sobol']['S1']); CI=SE['sobol']['ST_ci']
top=ST.sort_values(ascending=False).index[:8][::-1]; yy=np.arange(len(top))
a3.barh(yy+0.18,ST[top],0.34,color=BLUE,label=('Índice total (S$_T$)' if pt else 'Total-order index (S$_T$)'))
a3.errorbar(ST[top],yy+0.18,xerr=[[ST[t_]-CI[t_][0] for t_ in top],[CI[t_][1]-ST[t_] for t_ in top]],fmt='none',ecolor=INK,lw=0.8,capsize=2)
a3.barh(yy-0.18,S1[top].clip(lower=0),0.34,color='#86b6ef',label=('Índice de 1ª ordem (S$_1$)' if pt else 'First-order index (S$_1$)'))
a3.set_yticks(yy,[PN[t_][0 if pt else 1] for t_ in top],fontsize=8.5); a3.set_xlabel('Sobol')
a3.legend(frameon=False,fontsize=7.5,loc='lower right')
a3.set_title('(c) '+('Sobol: pesos que mudam a classe' if pt else 'Sobol: weights that change the class'),loc='left',color=INK,fontsize=10.5)
ps=np.load('data/p_severe_health.npy'); CLh=pd.read_pickle('data/final_cl.pkl')['Saude'].values
ordc={c:i_ for i_,c in enumerate(CLS)}; lev=np.array([ordc[c] for c in CLh]); o=np.lexsort((-ps,lev))
a4.bar(np.arange(len(ps)),ps[o],width=1.0,color=[ORD[l_] for l_ in lev[o]],linewidth=0)
pg=np.load('data/p_severe_global.npy'); a4.scatter(np.arange(len(ps)),pg[o],s=5,color=INK,zorder=3,label=('pesos aleatórios em todo o simplex' if pt else 'random weights over the whole simplex'))
for b_ in np.where(np.diff(lev[o])!=0)[0]: a4.axvline(b_+0.5,color='#b4b2ab',lw=0.6)
a4.set_xlim(-1,len(ps)); a4.set_ylim(0,1.03); a4.set_xticks([])
a4.set_ylabel('P(N3–N4)' if pt else 'P(L3–L4)'); a4.set_xlabel(('Amostras agrupadas pela classe na visão de saúde pública' if pt else 'Samples grouped by public-health class'))
from matplotlib.patches import Patch as _P
from matplotlib.lines import Line2D as _L
a4.legend(handles=[_P(color=ORD[i_],label=CLL[i_]) for i_ in range(5)]+[_L([],[],marker='o',ls='',color=INK,ms=3,label=('Dirichlet global' if pt else 'global Dirichlet'))],frameon=False,fontsize=7,ncol=2,loc='upper left')
a4.set_title('(d) '+('Monte Carlo: probabilidade de classe grave' if pt else 'Monte Carlo: probability of a severe class'),loc='left',color=INK,fontsize=10.5)
if pt:
    from matplotlib.ticker import FuncFormatter
    for a_ in (a2,a3,a4):
        a_.xaxis.set_major_formatter(FuncFormatter(lambda v,_: f'{v:g}'.replace('.',',')))
        if a_ is not a3: a_.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f'{v:g}'.replace('.',',')))
bump(fig,1.1); fig.subplots_adjust(left=0.1,right=0.98,top=0.95,bottom=0.08); fig.savefig(f'figs/{lang}_f6_robustez.png',dpi=400); plt.close()
# S2: leave-one-out
LO=SE['leave_one_out']; ks=sorted(LO,key=lambda k_:-LO[k_]['class_change_pct'])[:12][::-1]
fig,ax=plt.subplots(figsize=(8,5)); ax.barh([PN[k_][0 if pt else 1] for k_ in ks],[LO[k_]['class_change_pct'] for k_ in ks],color=[GC[GR[k_]] for k_ in ks],height=0.65)
for i_,k_ in enumerate(ks): ax.text(LO[k_]['class_change_pct']+0.5,i_,num2(LO[k_]['class_change_pct'],1)+'%',va='center',fontsize=8)
ax.set_xlabel('% '+('de amostras que mudam de classe ao retirar o parâmetro' if pt else 'of samples changing class when the parameter is removed'))
ax.legend(handles=[Patch(color=GC[g],label=GL[g][0 if pt else 1]) for g in ['MB','PC','HM']],frameon=False,loc='lower right')
bump(fig,1.1); fig.tight_layout(); fig.savefig(f'figs/{lang}_s2_loo.png',dpi=400); plt.close()
print('ok')
