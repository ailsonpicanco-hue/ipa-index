import sys; sys.path.insert(0,"scripts"); from bump import bump; import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely.geometry import shape
lang=sys.argv[1]
NAVY='#0d366b'; BLUE='#2a78d6'; OR='#eb6834'; INK='#0b0b0b'; MUT='#52514e'; BG='#fcfcfb'; LAND='#ecebe6'; EDGE='#a9a8a2'
plt.rcParams.update({'font.family':'DejaVu Sans','figure.facecolor':BG,'axes.facecolor':BG})
def polys(g):
    g=shape(g); return [g] if g.geom_type=='Polygon' else list(g.geoms)
def draw(ax,geom,fc,ec,lw=0.5,z=1):
    for p in polys(geom):
        x,y=p.exterior.xy; ax.fill(x,y,fc=fc,ec=ec,lw=lw,zorder=z)
br=json.load(open('geo/br_uf.json'))['features']; pa=json.load(open('geo/pa_mun.json'))['features']
fig=plt.figure(figsize=(12,5.2))
# A: Brazil
a=fig.add_axes([0.02,0.08,0.30,0.84])
for f in br: draw(a,f['geometry'],OR if f['properties']['SIGLA']=='PA' else LAND,EDGE,0.4)
a.set_aspect('equal'); a.axis('off'); a.set_title('(a) '+('Brasil – Pará' if lang=='pt' else 'Brazil – Pará State'),loc='left',fontsize=11,color=INK)
# B: Pará
b=fig.add_axes([0.33,0.08,0.30,0.84])
for f in pa:
    nm=f['properties']['name']; draw(b,f['geometry'],OR if nm=='Barcarena' else ('#cde2fb' if nm=='Belém' else LAND),EDGE,0.25)
b.set_aspect('equal'); b.axis('off'); b.set_title('(b) '+('Pará – Barcarena' if lang=='pt' else 'Pará – Barcarena municipality'),loc='left',fontsize=11,color=INK)
bb=shape([f for f in pa if f['properties']['name']=='Barcarena'][0]['geometry']).bounds
b.add_patch(plt.Rectangle((bb[0]-0.55,bb[1]-0.45),bb[2]-bb[0]+1.1,bb[3]-bb[1]+0.9,fill=False,ec=NAVY,lw=1.2,zorder=5))
# C: zoom
c=fig.add_axes([0.67,0.11,0.31,0.80])
x0,x1,y0,y1=bb[0]-0.55,bb[2]+0.55,bb[1]-0.45,bb[3]+0.45
for f in pa:
    g=shape(f['geometry']); 
    if g.bounds[2]<x0 or g.bounds[0]>x1 or g.bounds[3]<y0 or g.bounds[1]>y1: continue
    nm=f['properties']['name']; draw(c,f['geometry'],OR if nm=='Barcarena' else ('#cde2fb' if nm=='Belém' else LAND),EDGE,0.6)
    if nm in ('Abaetetuba','Moju','Acará','Ponta de Pedras'):
        pt=g.representative_point()
        if x0<pt.x<x1 and y0<pt.y<y1:
            c.text(pt.x,pt.y,nm,ha='center',va='center',fontsize=9 if nm!='Barcarena' else 10.5,fontweight='bold' if nm=='Barcarena' else 'normal',color=INK if nm!='Barcarena' else 'white',zorder=6)
for (lx,ly,lab,dx,dy) in [(-48.6258,-1.5058,'Barcarena' + (' (sede)' if lang=='pt' else ' (seat)'),-0.05,-0.07),(-48.4902,-1.4558,'Belém',0.04,0.05)]:
    c.plot(lx,ly,'o',ms=6,mfc='white',mec=NAVY,mew=1.6,zorder=7); c.text(lx+dx,ly+dy,lab,fontsize=9.5,fontweight='bold',color=NAVY,zorder=7,ha='right' if dx<0 else 'left',bbox=dict(boxstyle='round,pad=0.15',fc='white',ec='none',alpha=0.8))
c.set_xlim(x0,x1); c.set_ylim(y0,y1); c.set_aspect('equal')
for s in c.spines.values(): s.set_color(NAVY)
c.tick_params(labelsize=8,colors=MUT); c.set_xticks(np.arange(-49.2,-47.9,0.4)); c.set_xlabel('Longitude',fontsize=8,color=MUT); c.set_ylabel('Latitude',fontsize=8,color=MUT)
c.set_title('(c) '+('Barcarena: 165 poços (2018)' if lang=='pt' else 'Barcarena: 165 wells (2018)'),loc='left',fontsize=11,color=INK)
# north arrow & scale (approx 1° lat ≈ 111 km)
c.annotate('N',xy=(x1-0.12,y1-0.08),xytext=(x1-0.12,y1-0.30),ha='center',fontsize=10,fontweight='bold',arrowprops=dict(arrowstyle='-|>',color=INK),color=INK)
sx=x0+0.1; sy=y0+0.08; km20=20/111.0
c.plot([sx,sx+km20],[sy,sy],color=INK,lw=3); c.text(sx+km20/2,sy+0.05,'20 km',ha='center',fontsize=8,color=INK)
fig.text(0.02,0.01,('Fonte dos limites: IBGE (via geodata-br). Sede municipal: 01°30′21″S, 48°37′33″W.\nBairros amostrados: Vila Itupanema, Jardim Cabano e Laranjal (Pantoja, 2021).' if lang=='pt' else
 'Boundaries: IBGE (via geodata-br). Municipal seat: 01°30′21″S, 48°37′33″W.\nSampled neighbourhoods: Vila Itupanema, Jardim Cabano and Laranjal (Pantoja, 2021).'),fontsize=7.5,color=MUT)
bump(fig,1.35); fig.savefig(f'figs/{lang}_f2_area.png',dpi=400); print('ok')
