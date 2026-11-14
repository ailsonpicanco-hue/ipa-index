# IPA – Water Potability Index

Reference implementation, data and reproduction scripts for:

> Ribeiro, H.M.C., Picanço, A.R.S., et al. *A water potability index for the Brazilian Amazon based on a goal programming model.* Submitted to the *Journal of Environmental Management* (2026).

The IPA is an **additive excess index** anchored on the Brazilian potability standard (Ordinance GM/MS 888/2021):

* **IPA = 0** if and only if the sample complies with every measured limit;
* the index grows with the **number and magnitude** of exceedances, in three components:
  physicochemical (PC), microbiological (MB) and heavy metals (HM);
* **missing parameters contribute nothing**: the IPA is still computable, becomes a lower bound
  and is reported with its **coverage** C (share of total weight measured);
* a **legal veto** (E. coli or any Annex 9 substance above its limit) places the sample at Level 3 or above;
* weights come from **goal programming**, which blends unsupervised CRITIC weights with four
  management lenses (public health, sanitation, treatability, legal compliance).

| Class | IPA | Management reading |
|---|---|---|
| Potable | 0 | surveillance |
| Non-potable – Level 1 | 0–75 | simple correction |
| Non-potable – Level 2 | 75–150 | conventional treatment |
| Non-potable – Level 3 | 150–225 or legal veto | advanced treatment / alternative source |
| Non-potable – Level 4 | > 225 | immediate alternative supply |

## Quick start

```bash
pip install -r requirements.txt
python scripts/reproduce.py          # reproduces weights, classes, SMAA and the missing-metals test
```

```python
import pandas as pd, ipa
df = pd.read_csv('data/barcarena_2018_wells.csv')          # one row per sample; missing columns are allowed
w  = pd.read_csv('data/final_weights.csv', index_col=0)['health']
res = ipa.ipa(df, w)                                         # IPA, components, coverage, level, class, partial
res.head()
```

Parameter codes: `amonia, nitrito, nitrato, dureza, cloreto, cor, pH, SDT, sulfato, turbidez, na` (PC);
`ct, ec` (MB, 1 = present, 0 = absent); `al, ba, cd, pb, cu, cr, fe, mn, ni, zn, hg` (HM). Units: mg/L
(colour in Hazen units, turbidity in NTU).

## Contents

| Path | Content |
|---|---|
| `ipa/core.py` | excursion, IPA, coverage, legal veto, classification, CRITIC, entropy, goal programming, SMAA |
| `ipa/lenses.py` | priority tiers of each management lens and the rule behind them; expert weights |
| `data/barcarena_2018_wells.csv` | 165 well samples, Barcarena (Pará), 2018 – LACEN-PA, compiled by Pantoja (2021) |
| `data/final_weights.csv` | final weights of the five lenses and of the purely data-driven methods |
| `data/review/` | PRISMA 2020 review: search log, flow counts, synthesis and the 370 included studies (DOIs verified in Crossref) |
| `scripts/reproduce.py` | short reproduction of the main results with the package |
| `scripts/paper/` | full analysis scripts used for the article (model, sensitivity analyses, figures, spreadsheet) |
| `spreadsheet/IPA_calculator.xlsx` | spreadsheet calculator with a lens selector (formulas, no macros) |
| `notebooks/IPA_example.ipynb` | worked example |

The pseudocode of the method (Algorithms S1–S3) is in the Supplementary material of the article.

## Licence

Code: MIT. Data: CC BY 4.0. Please cite the article and this repository (see `CITATION.cff`).
