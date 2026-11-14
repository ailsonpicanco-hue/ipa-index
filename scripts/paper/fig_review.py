import sys; sys.path.insert(0,"scripts"); from bump import bump; import json, numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from shapely.geometry import shape
lang=sys.argv[1]; pt=lang=='pt'
NAVY='#0d366b'; BLUE='#2a78d6'; LB='#cde2fb'; OR='#eb6834'; INK='#0b0b0b'; MUT='#52514e'; BG='#fcfcfb'; LAND='#ecebe6'; EDGE='#c9c8c2'
plt.rcParams.update({'font.family':'DejaVu Sans','figure.facecolor':BG,'axes.facecolor':BG,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#8a8984','xtick.color':MUT,'ytick.color':MUT})
fl=json.load(open('prisma/flow_stage1.json')); S=json.load(open('prisma/synthesis.json')); log=json.load(open('prisma/search_log.json'))
fmt=lambda n: f'{n:,}'.replace(',', '.' if pt else ',')
# ---------- PRISMA flow
fig=plt.figure(figsize=(9,8.4)); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis('off')
def box(x,y,w,h,txt,fc='white',ec=BLUE,bold=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.3,rounding_size=1',fc=fc,ec=ec,lw=1.4)); ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=8.8,color=INK,fontweight='bold' if bold else 'normal',linespacing=1.35)
def arr(a,b): ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=14,color=MUT,lw=1.2))
q=[log['Q1_core']['total'],log['Q2_methods']['total'],log['Q3_brazil']['total']]
stage=[('Identificação' if pt else 'Identification',84),('Triagem' if pt else 'Screening',52),('Inclusão' if pt else 'Included',8)]
for t,y in stage:
    ax.add_patch(FancyBboxPatch((1,y-4),6,18 if y>10 else 10,boxstyle='round,pad=0.2,rounding_size=1',fc=NAVY,ec=NAVY)); ax.text(4,y+5 if y>10 else y+1,t,rotation=90,ha='center',va='center',color='white',fontsize=9,fontweight='bold')
box(10,82,46,14,(f"Registros identificados no Semantic Scholar\n(n = {fmt(fl['identified'])}; Q1 = {fmt(q[0])}, Q2 = {fmt(q[1])}, Q3 = {fmt(q[2])})" if pt else
                 f"Records identified in Semantic Scholar\n(n = {fmt(fl['identified'])}; Q1 = {fmt(q[0])}, Q2 = {fmt(q[1])}, Q3 = {fmt(q[2])})"))
box(62,82,36,14,(f"Removidos antes da triagem:\nduplicados (n = {fmt(fl['duplicates_removed']+fl['dup_doi_removed'])})\nsem DOI (n = {fmt(fl['no_doi_removed'])})" if pt else
                 f"Removed before screening:\nduplicates (n = {fmt(fl['duplicates_removed']+fl['dup_doi_removed'])})\nno DOI (n = {fmt(fl['no_doi_removed'])})"))
arr((56,89),(62,89)); arr((33,82),(33,72))
box(10,60,46,12,(f"Registros triados (título e resumo)\n(n = {fmt(fl['screened'])})" if pt else f"Records screened (title and abstract)\n(n = {fmt(fl['screened'])})"))
box(62,60,36,12,(f"Excluídos fora do escopo\n(não índice de qualidade da água;\nar, solo, sedimento, marinho) (n = {fmt(fl['excluded_title_abstract_scope'])})" if pt else
                 f"Excluded, out of scope\n(not a water quality index;\nair, soil, sediment, marine) (n = {fmt(fl['excluded_title_abstract_scope'])})"))
arr((56,66),(62,66)); arr((33,60),(33,50))
excl2=fl['assessed_eligibility']-fl['eligible_auto']
box(10,38,46,12,(f"Avaliados para elegibilidade\n(n = {fmt(fl['assessed_eligibility'])})" if pt else f"Assessed for eligibility\n(n = {fmt(fl['assessed_eligibility'])})"))
box(62,32,36,24,(f"Excluídos (n = {fmt(excl2+fl['excluded_eligibility_tightened']+fl['excluded_irrigation_drastic_soil']+fl['crossref_failed'])}):\nsem contribuição metodológica\nou de apoio à decisão\n(n = {fmt(excl2-fl.get('no_abs',0))})\nirrigação, DRASTIC, solo (n = {fmt(fl['excluded_irrigation_drastic_soil']+fl['excluded_eligibility_tightened'])})\nDOI não confirmado no\nCrossref (n = {fl['crossref_failed']})" if pt else
                 f"Excluded (n = {fmt(excl2+fl['excluded_eligibility_tightened']+fl['excluded_irrigation_drastic_soil']+fl['crossref_failed'])}):\nno methodological or\ndecision-support contribution\n(n = {fmt(excl2)})\nirrigation, DRASTIC, soil (n = {fmt(fl['excluded_irrigation_drastic_soil']+fl['excluded_eligibility_tightened'])})\nDOI not confirmed in\nCrossref (n = {fl['crossref_failed']})"))
arr((56,44),(62,44)); arr((33,38),(33,18))
box(10,6,46,12,(f"Estudos incluídos na síntese\n(n = {S['n_included']}), todos com DOI\nconferido no Crossref" if pt else f"Studies included in the synthesis\n(n = {S['n_included']}), all with DOI\nverified in Crossref"),fc=LB,ec=NAVY,bold=True)
bump(fig,1.3); fig.savefig(f'figs/{lang}_f3_prisma.png',dpi=400); plt.close()
# ---------- synthesis figure
w=json.load(open('geo/world.json'))['features']
cnt=pd.Series(S['countries']); name_map={'United States':'United States of America','South Korea':'South Korea'}
fig=plt.figure(figsize=(12,7.6))
a=fig.add_axes([0.02,0.50,0.62,0.47]); 
from matplotlib.colors import LinearSegmentedColormap, LogNorm
cm=LinearSegmentedColormap.from_list('b',['#cde2fb','#86b6ef','#3987e5','#1c5cab','#0d366b']); norm=LogNorm(1,cnt.max())
for f in w:
    nm=f['properties']['name']; k=[c for c in cnt.index if name_map.get(c,c)==nm]
    g=shape(f['geometry']); gs=[g] if g.geom_type=='Polygon' else list(g.geoms)
    col=cm(norm(cnt[k[0]])) if k else LAND
    for p in gs:
        x,y=p.exterior.xy; a.fill(x,y,fc=col,ec='white',lw=0.2)
a.set_xlim(-170,180); a.set_ylim(-58,84); a.set_aspect('equal'); a.axis('off')
a.set_title(('(a) País de estudo citado no resumo' if pt else '(a) Study country named in the abstract')+f' (n = {S["country_identified"]})',loc='left',fontsize=10.5,color=INK)
sm=plt.cm.ScalarMappable(norm=norm,cmap=cm); cax=fig.add_axes([0.20,0.475,0.26,0.015]); cb=fig.colorbar(sm,cax=cax,orientation='horizontal'); cb.set_ticks([1,2,5,10,20,50]); cb.set_ticklabels(['1','2','5','10','20','50']); cb.ax.tick_params(labelsize=7.5); cax.set_title('Nº de estudos (escala log)' if pt else 'No. of studies (log scale)',fontsize=8,color=MUT,pad=3)
# year
b=fig.add_axes([0.70,0.52,0.28,0.40]); yrs=pd.Series({int(k):v for k,v in S['by_year'].items()}).sort_index()
b.bar(yrs.index,yrs.values,color=BLUE,width=0.8); b.set_title('(b) '+('Estudos por ano' if pt else 'Studies per year'),loc='left',fontsize=10.5,color=INK)
b.tick_params(labelsize=8); b.set_xticks([2010,2014,2018,2022,2026]); b.yaxis.grid(True,color='#e6e5e0'); b.set_axisbelow(True)
b.text(0.02,0.92,('2026: até a data da busca' if pt else '2026: up to search date'),transform=b.transAxes,fontsize=7.5,color=MUT)
# aggregation
lab_agg={'Aprendizado de máquina':('Aprendizado de máquina','Machine learning'),'Fuzzy':('Lógica fuzzy','Fuzzy logic'),'Aditiva (média/soma ponderada)':('Aditiva (soma/média ponderada)','Additive (weighted sum/mean)'),
 'CCME / vetorial':('CCME (vetorial)','CCME (vector)'),'Multiplicativa (geométrica)':('Multiplicativa (geométrica)','Multiplicative (geometric)'),'Mínimo / pior caso':('Mínimo / pior caso','Minimum / worst case')}
c=fig.add_axes([0.25,0.07,0.23,0.30]); ag=pd.Series(S['aggregation']).sort_values()
c.barh([lab_agg[k][0 if pt else 1] for k in ag.index],ag.values,color=BLUE,height=0.6)
for i,v in enumerate(ag.values): c.text(v+2,i,f'{v} ({100*v/S["n_included"]:.0f}%)',va='center',fontsize=8,color=INK)
c.set_title('(c) '+('Forma de agregação / modelagem' if pt else 'Aggregation / modelling approach'),loc='left',fontsize=10.5,color=INK); c.tick_params(labelsize=8.5); c.set_xlim(0,ag.max()*1.3)
lab_w={'Entropia':('Entropia','Entropy'),'PCA / análise fatorial':('PCA / análise fatorial','PCA / factor analysis'),'Especialistas / Delphi':('Especialistas / Delphi','Experts / Delphi'),'AHP / ANP':('AHP / ANP','AHP / ANP'),
 'Programação por metas / otimização':('Otimização / prog. por metas','Optimisation / goal programming'),'Aprendizado de máquina (SHAP etc.)':('Importância em ML (SHAP)','ML importance (SHAP)'),'CRITIC':('CRITIC','CRITIC'),'Pesos iguais / sem pesos':('Pesos iguais','Equal weights')}
d=fig.add_axes([0.70,0.07,0.25,0.30]); wt=pd.Series(S['weighting']).sort_values()
d.barh([lab_w[k][0 if pt else 1] for k in wt.index],wt.values,color=OR,height=0.6)
for i,v in enumerate(wt.values): d.text(v+1,i,f'{v} ({100*v/S["n_included"]:.0f}%)',va='center',fontsize=8,color=INK)
d.set_title('(d) '+('Método de ponderação' if pt else 'Weighting method'),loc='left',fontsize=10.5,color=INK); d.tick_params(labelsize=8.5); d.set_xlim(0,wt.max()*1.35)
fig.text(0.02,0.005,(f"Categorias não exclusivas, codificadas por termos no título e resumo (n = {S['n_included']}). Precisão da triagem em amostra aleatória: 85%." if pt else
 f"Non-exclusive categories coded from title and abstract terms (n = {S['n_included']}). Screening precision in a random sample: 85%."),fontsize=7.5,color=MUT)
bump(fig,1.3); fig.savefig(f'figs/{lang}_f4_revisao.png',dpi=400); print('ok')
