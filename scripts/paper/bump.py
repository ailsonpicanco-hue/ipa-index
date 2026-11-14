import matplotlib.text as mt
def bump(fig,k):
    for t in fig.findobj(mt.Text):
        try: t.set_fontsize(t.get_fontsize()*k)
        except Exception: pass
