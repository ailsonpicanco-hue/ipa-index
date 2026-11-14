import sys; sys.path.insert(0,'scripts')
from load import *
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation
df=pd.read_pickle('data/results.pkl'); WT=pd.read_csv('data/final_weights.csv',index_col=0)
FI=pd.read_pickle('data/final_ipa.pkl'); FC=pd.read_pickle('data/final_cl.pkl')
df=df[[c for c in df.columns if not (c.startswith('IPA_') or c.startswith('Classe_'))]]
for c in FI.columns: df['IPA_'+c]=FI[c]; df['Classe_'+c]=FC[c]
cols=['amonia','nitrito','nitrato','dureza','cloreto','cor','pH','SDT','sulfato','turbidez','ct','ec','al','ba','cd','pb','cu','cr','fe','mn','ni','na','zn','hg']
nice={'amonia':'Amônia (mg/L)','nitrito':'Nitrito (mg/L)','nitrato':'Nitrato (mg/L)','dureza':'Dureza (mg/L)','cloreto':'Cloreto (mg/L)','cor':'Cor aparente (uH)','pH':'pH','SDT':'SDT (mg/L)','sulfato':'Sulfato (mg/L)','turbidez':'Turbidez (uT)','ct':'Coliformes totais (1=presente)','ec':'E. coli (1=presente)','al':'Al (mg/L)','ba':'Ba (mg/L)','cd':'Cd (mg/L)','pb':'Pb (mg/L)','cu':'Cu (mg/L)','cr':'Cr (mg/L)','fe':'Fe (mg/L)','mn':'Mn (mg/L)','ni':'Ni (mg/L)','na':'Na (mg/L)','zn':'Zn (mg/L)','hg':'Hg (mg/L) – não analisado'}
VM=dict(VMP); VM['hg']=0.001
GR={**{k:'Físico-químico' for k in ['amonia','nitrito','nitrato','dureza','cloreto','cor','pH','SDT','sulfato','turbidez','na']},'ct':'Microbiológico','ec':'Microbiológico',**{k:'Metais' for k in ['al','ba','cd','pb','cu','cr','fe','mn','ni','zn','hg']}}
AN9=['nitrato','nitrito','ba','cd','pb','cu','cr','ni','hg']
W2=WT.copy(); W2.loc['hg']=W2.loc['pb']; W2.loc['hg','S0_Especialistas']=1.0
SC=list(WT.columns)
F=Font(name='Arial',size=10); FB=Font(name='Arial',size=10,bold=True); FBLUE=Font(name='Arial',size=10,color='0000FF'); FG=Font(name='Arial',size=10,color='008000')
HDR=PatternFill('solid',fgColor='DCE6F1'); YEL=PatternFill('solid',fgColor='FFFF00')
wb=Workbook()
# README
ws=wb.active; ws.title='LEIAME'
txt=["IPA – Índice de Potabilidade da Água, versão aditiva de excedência (proposta revista)",
"Dados: 165 amostras de poços, Barcarena-PA, 2018 (planilha bruta enviada pelo autor). Hg não foi analisado: coluna vazia, para ilustrar parâmetro faltante.",
"",
"COMO USAR",
"1. Na aba Parametros, escolha o cenário ativo na célula amarela C2 (1 a 7). Todos os cálculos se atualizam.",
"2. Os pesos (texto azul) podem ser editados para testar novas ponderações. Os VMPs seguem a Portaria GM/MS 888/2021.",
"3. Na aba Dados, apagar um valor simula parâmetro faltante: a excursão vira 0 e a cobertura da amostra cai.",
"",
"MÉTODO",
"Excursão (parâmetros com VMP máximo): x = 100·(1 − VMP/v) se v > VMP, senão 0. Equivale a 100·e/(1+e), com e = v/VMP − 1. Não satura em 2×VMP.",
"pH: e = 6 − pH (se pH<6) ou pH − 9 (se pH>9); x = 100·e/(1+e). Microbiológicos: x = 100 se presente.",
"IPA = Σ peso·x, decomposto em Físico-químico + Microbiológico + Metais (aditivo).",
"Camada 1 (veto legal): E. coli presente ou qualquer excedência do Anexo 9 (nitrato, nitrito, Ba, Cd, Pb, Cu, Cr, Ni, Hg) → classe mínima Nível 3.",
"Cobertura = soma dos pesos dos parâmetros medidos ÷ soma de todos os pesos. 'Potável' com cobertura < 100% deve ser lido como 'sem penalidade observada (IPA parcial)'.",
"Classes: Potável (0); Nível 1 (≤75); Nível 2 (≤150); Nível 3 (≤225); Nível 4 (>225).",
"",
"CENÁRIOS DE PESO",
"Especialistas: pesos da v12 ajustados por GP. Saude, Saneamento, Tratabilidade, Conformidade: faixas 1,0/0,6/0,2 por visão, conciliadas com CRITIC por programação por metas (λ = 0,7).",
"CRITIC_puro e Entropia_pura: pesos não supervisionados, só para contraste (refletem variabilidade, não risco). Cenário 2 = Saúde pública (visão principal do artigo).",
"",
"A aba Resultados_script traz os valores calculados em Python (todos os cenários, SMAA, CCME, cluster) para conferência."]
for i,t in enumerate(txt,1):
    c=ws.cell(i,1,t); c.font=FB if t.isupper() or i==1 else F
ws.column_dimensions['A'].width=140
# Parametros
wp=wb.create_sheet('Parametros')
wp['A1']='Cenário ativo (1–7):'; wp['A1'].font=FB
wp['C2']=1; wp['C2'].fill=YEL; wp['C2'].font=FBLUE; wp['B2']='Nº do cenário →'; wp['B2'].font=F
wp['D2']='=INDEX(F4:L4,1,C2)'; wp['D2'].font=FB
dv=DataValidation(type='whole',operator='between',formula1='1',formula2='7'); wp.add_data_validation(dv); dv.add('C2')
hdr=['Código','Parâmetro','Grupo','VMP (Portaria 888)','Anexo 9 (veto)']+[s.replace('_',' ') for s in SC]+['Peso ativo']
for j,h in enumerate(hdr,1):
    c=wp.cell(4,j,h); c.font=FB; c.fill=HDR; c.alignment=Alignment(wrap_text=True)
for i,k in enumerate(cols):
    r=5+i
    wp.cell(r,1,k).font=F; wp.cell(r,2,nice[k]).font=F; wp.cell(r,3,GR[k]).font=F
    c=wp.cell(r,4,'6,0–9,0' if k=='pH' else ('Ausência' if k in ('ct','ec') else VM[k])); c.font=FBLUE
    wp.cell(r,5,1 if k in AN9 else 0).font=F
    for j,s in enumerate(SC):
        c=wp.cell(r,6+j,round(float(W2.loc[k,s]),6)); c.font=FBLUE; c.number_format='0.000'
    c=wp.cell(r,6+len(SC),f'=INDEX(F{r}:L{r},1,$C$2)'); c.font=F; c.number_format='0.000'
NP=len(cols); last=4+NP
wp.cell(last+2,1,'Soma dos pesos ativos').font=FB; wp.cell(last+2,13,f'=SUM(M5:M{last})').number_format='0.000'
for j,w in enumerate([10,30,16,14,10]+[13]*len(SC)+[11],1): wp.column_dimensions[L(j)].width=w
wp.freeze_panes='C5'
# Dados
wd=wb.create_sheet('Dados')
wd.cell(1,1,'Amostra').font=FB; wd.cell(1,1).fill=HDR
for j,k in enumerate(cols,2):
    c=wd.cell(1,j,nice[k]); c.font=FB; c.fill=HDR; c.alignment=Alignment(wrap_text=True)
for i in range(len(df)):
    wd.cell(i+2,1,i+1).font=F
    for j,k in enumerate(cols,2):
        if k=='hg': continue
        v=df.iloc[i][k]; c=wd.cell(i+2,j,float(v) if k not in ('ct','ec') else int(v)); c.font=FBLUE
wd.freeze_panes='B2'
for j in range(1,len(cols)+2): wd.column_dimensions[L(j)].width=12
# Excursao
we=wb.create_sheet('Excursao')
we.cell(1,1,'Amostra').font=FB
for j,k in enumerate(cols,2):
    c=we.cell(1,j,k); c.font=FB; c.fill=HDR
    pr=5+cols.index(k)
    c2=we.cell(2,j,f'=Parametros!M{pr}'); c2.font=FG; c2.number_format='0.000'   # active weight row
we.cell(2,1,'peso ativo →').font=F
N=len(df)
for i in range(N):
    r=i+3; dr=i+2; we.cell(r,1,i+1).font=F
    for j,k in enumerate(cols,2):
        d=f'Dados!{L(j)}{dr}'; pr=5+cols.index(k); vmp=f'Parametros!$D${pr}'
        if k=='pH':
            f=f'=IF(ISNUMBER({d}),IF({d}<6,100*(6-{d})/(1+6-{d}),IF({d}>9,100*({d}-9)/(1+{d}-9),0)),0)'
        elif k in ('ct','ec'):
            f=f'=IF(ISNUMBER({d}),100*{d},0)'
        else:
            f=f'=IF(ISNUMBER({d}),IF({d}>{vmp},100*(1-{vmp}/{d}),0),0)'
        c=we.cell(r,j,f); c.font=F; c.number_format='0.0'
we.freeze_panes='B3'
# IPA
wi=wb.create_sheet('IPA')
H=['Amostra','Físico-químico','Microbiológico','Metais','IPA total','Classe (camada 2)','Veto legal (EC ou Anexo 9)','Classe final','Cobertura','Leitura']
for j,h in enumerate(H,1):
    c=wi.cell(1,j,h); c.font=FB; c.fill=HDR; c.alignment=Alignment(wrap_text=True)
gcols={g:[cols.index(k)+2 for k in cols if GR[k]==g] for g in ['Físico-químico','Microbiológico','Metais']}
for i in range(N):
    r=i+2; er=i+3; dr=i+2
    wi.cell(r,1,i+1).font=F
    for j,g in enumerate(['Físico-químico','Microbiológico','Metais'],2):
        terms='+'.join(f'Excursao!{L(c)}{er}*Excursao!{L(c)}$2' for c in gcols[g])
        cc=wi.cell(r,j,'='+terms); cc.font=F; cc.number_format='0.0'
    wi.cell(r,5,f'=SUM(B{r}:D{r})').number_format='0.0'
    wi.cell(r,6,f'=IF(E{r}=0,"Potável",IF(E{r}<=75,"Nível 1",IF(E{r}<=150,"Nível 2",IF(E{r}<=225,"Nível 3","Nível 4"))))')
    a9=[cols.index(k)+2 for k in AN9]
    conds=[f'Dados!{L(cols.index("ec")+2)}{dr}=1']+[f'AND(ISNUMBER(Dados!{L(c)}{dr}),Dados!{L(c)}{dr}>Parametros!$D${5+c-2})' for c in a9]
    wi.cell(r,7,f'=IF(OR({",".join(conds)}),"Sim","Não")')
    wi.cell(r,8,f'=IF(AND(G{r}="Sim",OR(F{r}="Potável",F{r}="Nível 1",F{r}="Nível 2")),"Nível 3",F{r})')
    covterms='+'.join(f'ISNUMBER(Dados!{L(c)}{dr})*Excursao!{L(c)}$2' for c in range(2,len(cols)+2))
    wi.cell(r,9,f'=({covterms})/SUM(Excursao!$B$2:${L(len(cols)+1)}$2)').number_format='0%'
    wi.cell(r,10,f'=IF(AND(H{r}="Potável",I{r}<0.9999),"Sem penalidade observada (IPA parcial)",H{r})')
    for j in range(1,11): wi.cell(r,j).font=F
wi.freeze_panes='B2'
for j,w in enumerate([9,13,13,10,10,14,14,12,10,36],1): wi.column_dimensions[L(j)].width=w
# Resumo
wr=wb.create_sheet('Resumo')
wr['A1']='Cenário ativo:'; wr['A1'].font=FB; wr['B1']='=Parametros!D2'; wr['B1'].font=FG
wr['A3']='Classe final'; wr['B3']='Nº amostras'; wr['C3']='%'
for c in ('A3','B3','C3'): wr[c].font=FB; wr[c].fill=HDR
for i,k in enumerate(ORDER):
    r=4+i; wr.cell(r,1,k).font=F
    wr.cell(r,2,f'=COUNTIF(IPA!$H$2:$H${N+1},A{r})').font=F
    c=wr.cell(r,3,f'=B{r}/{N}'); c.number_format='0.0%'; c.font=F
wr.cell(9,1,'Total').font=FB; wr.cell(9,2,'=SUM(B4:B8)').font=FB
wr.cell(11,1,'Amostras com veto legal').font=F; wr.cell(11,2,f'=COUNTIF(IPA!G2:G{N+1},"Sim")')
wr.cell(12,1,'Cobertura média').font=F; c=wr.cell(12,2,f'=AVERAGE(IPA!I2:I{N+1})'); c.number_format='0.0%'
wr.cell(13,1,'Participação no IPA – Físico-químico').font=F; c=wr.cell(13,2,f'=SUM(IPA!B2:B{N+1})/SUM(IPA!E2:E{N+1})'); c.number_format='0.0%'
wr.cell(14,1,'Participação no IPA – Microbiológico').font=F; c=wr.cell(14,2,f'=SUM(IPA!C2:C{N+1})/SUM(IPA!E2:E{N+1})'); c.number_format='0.0%'
wr.cell(15,1,'Participação no IPA – Metais').font=F; c=wr.cell(15,2,f'=SUM(IPA!D2:D{N+1})/SUM(IPA!E2:E{N+1})'); c.number_format='0.0%'
wr.column_dimensions['A'].width=40; wr.column_dimensions['B'].width=22
# Resultados_script (static)
ws2=wb.create_sheet('Resultados_script')
out=df[['IPA','cls','compliant_888','veto','CCME','WAWQI','SMAA_maxprob','cluster']+[c for c in df.columns if c.startswith('IPA_') or c.startswith('Classe_')]].copy()
out.columns=['IPA_v12_reproduzido','Classe_v12_reproduzida','Conforme_Portaria_888','Veto_legal','CCME_WQI','WAWQI','SMAA_prob_classe_modal_(versao_anterior)','Cluster_kmeans']+[c for c in out.columns[8:]]
ws2.cell(1,1,'Amostra').font=FB
for j,h in enumerate(out.columns,2): c=ws2.cell(1,j,h); c.font=FB; c.fill=HDR; c.alignment=Alignment(wrap_text=True)
for i in range(N):
    ws2.cell(i+2,1,i+1).font=F
    for j,h in enumerate(out.columns,2):
        v=out.iloc[i][h]
        if isinstance(v,(bool,np.bool_)): v='Sim' if v else 'Não'
        elif isinstance(v,(float,np.floating)): v=round(float(v),2)
        elif isinstance(v,(np.integer,)): v=int(v)
        ws2.cell(i+2,j,v).font=F
ws2.cell(N+3,1,'Valores calculados por script Python (estáticos), para conferência com as abas de fórmulas no cenário S0.').font=Font(name='Arial',size=9,italic=True)
ws2.freeze_panes='B2'
wb.save('IPA_Barcarena_modelo_revisto.xlsx'); print('saved')
