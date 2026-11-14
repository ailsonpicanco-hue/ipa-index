import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'mathtext.fontset':'stix','font.family':'STIXGeneral'})
E={'en':{
1:r'$x_{ij}=100\,\dfrac{e_{ij}}{1+e_{ij}}=100\left(1-\dfrac{\mathrm{MAV}_i}{v_{ij}}\right)\ \ \mathrm{if}\ v_{ij}>\mathrm{MAV}_i;\qquad x_{ij}=0\ \ \mathrm{otherwise}$',
2:r'$\mathrm{IPA}_j=\sum_{i\in M_j} w_i\,x_{ij}=\mathrm{IPA}_j^{\,PC}+\mathrm{IPA}_j^{\,MB}+\mathrm{IPA}_j^{\,HM}$',
3:r'$C_j=\dfrac{\sum_{i\in M_j} w_i}{\sum_{i\in P} w_i}$',
4:r'$c_i=\sigma_i\sum_{k}\left(1-r_{ik}\right),\qquad w_i^{\,CRITIC}=\dfrac{c_i}{\sum_k c_k}$',
5:[r'$\min\ Z=\sum_i\left(d_i^{+}+d_i^{-}\right)\quad \mathrm{s.t.}\quad w_i-d_i^{+}+d_i^{-}=t_i^{L};\quad \sum_i w_i=\sum_i w_i^{L}$',
   r'$w_a\geq w_b+0.1\ \ \forall\, a\in T_k,\ b\in T_{k+1};\quad w_{EC}\geq w_c\ \ \forall\ \mathrm{chemical}\ c;\quad 0.05\leq w_i\leq 1.5;\quad d_i^{+},d_i^{-}\geq 0$']},
'pt':{
1:r'$x_{ij}=100\,\dfrac{e_{ij}}{1+e_{ij}}=100\left(1-\dfrac{\mathrm{VMP}_i}{v_{ij}}\right)\ \ \mathrm{se}\ v_{ij}>\mathrm{VMP}_i;\qquad x_{ij}=0\ \ \mathrm{caso\ contr\acute{a}rio}$',
2:r'$\mathrm{IPA}_j=\sum_{i\in M_j} w_i\,x_{ij}=\mathrm{IPA}_j^{\,FQ}+\mathrm{IPA}_j^{\,MB}+\mathrm{IPA}_j^{\,MP}$',
3:r'$C_j=\dfrac{\sum_{i\in M_j} w_i}{\sum_{i\in P} w_i}$',
4:r'$c_i=\sigma_i\sum_{k}\left(1-r_{ik}\right),\qquad w_i^{\,CRITIC}=\dfrac{c_i}{\sum_k c_k}$',
5:[r'$\min\ Z=\sum_i\left(d_i^{+}+d_i^{-}\right)\quad \mathrm{s.a.}\quad w_i-d_i^{+}+d_i^{-}=t_i^{L};\quad \sum_i w_i=\sum_i w_i^{L}$',
   r'$w_a\geq w_b+0{,}1\ \ \forall\, a\in T_k,\ b\in T_{k+1};\quad w_{EC}\geq w_c\ \ \forall\ \mathrm{qu\acute{\i}mico}\ c;\quad 0{,}05\leq w_i\leq 1{,}5;\quad d_i^{+},d_i^{-}\geq 0$']}}
for L,d in E.items():
    for n,s in d.items():
        lines=s if isinstance(s,list) else [s]
        h=0.6*len(lines)+0.2
        fw=7.6 if len(lines)>1 else 6.3
        fig=plt.figure(figsize=(fw,h)); 
        for k,ln in enumerate(lines):
            fig.text(0.46,1-(k+0.55)/(len(lines)+0.1),ln,ha='center',va='center',fontsize=12.5 if len(lines)==1 else 11.5)
        fig.text(0.99,0.5,f'({n})',ha='right',va='center',fontsize=12.5)
        fig.savefig(f'figs/{L}_eq{n}.png',dpi=400,facecolor='white'); plt.close()
print('ok')
