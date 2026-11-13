"""USD planning envelopes, not a supplier quote. Five paired panels, ONE pitch.
Published assembly rates checked 2026-11-13; material/tool/labor ranges are
explicit analyst allocations. Regenerate rather than rounding intermediate sums.
"""
from pathlib import Path
import json,csv
E=Path(__file__).resolve().parent;BASE=E.parent/'issue-200-wing-rev3'
bom=list(csv.DictReader((BASE/'panel-17mm/bom.csv').open()));qty={r['Comment']:int(r['Quantity']) for r in bom}
unit={'DRV5055A3QDBZR':[.8,1.6],'TMUX1208PWR':[.25,.8],'BM14B-GHS-TBT(LF)(SN)':[.8,2.],'GRM188R71C104KA01D':[.01,.04]}
parts=[sum(qty[k]*v[i] for k,v in unit.items())*5 for i in (0,1)]
# Including the two metal mounting solder lands per GH, no bare test pads/NPTH.
joints=42*3+48*2+6*16+2*(14+2);smt=joints*5*.0016
bare=[30,60] # Rev.4 pair panel not quoted: allow area/rails/NPTH changes vs #133.
fees=dict(economic_setup=8.18,economic_stencil=1.53,standard_double_setup=51.12,standard_double_stencil=16.42,panel=8.21,economic_feeder_type=3.07,standard_feeder_type=1.53,standard_rigid_fixture_5panels=16.42,standard_packing_allowance=.55)
fixedeco=[8.18+1.53+8.21+smt+3*3.07,8.18+1.53+8.21+smt+4*3.07]
fixedstd=[51.12+16.42+8.21+smt+4*1.53+16.42+.55]*2
rows=[]
for name,other in [('Rev4 Economic one side',fixedeco),('Rev3 Standard two sides',fixedstd),('Hand hot plate, tools owned',[20,45]),('Hand hot plate, buy kit',[60,165])]:
 cash=[bare[i]+parts[i]+other[i] for i in (0,1)]
 rows.append(dict(method=name,batch_cash_usd=cash,per_pair_cash_usd=[c/5 for c in cash]))
manualtime=[15,30];labor=[15,30];kit_owned=rows[2]['batch_cash_usd'];kit_new=rows[3]['batch_cash_usd']
out=dict(currency='USD',quantity='5 assembled left/right panels = 10 Wings, one pitch only',basis_urls=['https://jlcpcb.com/help/article/pcb-assembly-price','https://jlcpcb.com/capabilities/pcb-assembly-capabilities'],historical_bare_basis='docs/issue-133-wing-cost-check.md ($9.30/$9.90 per five OLD single Wings, NOT Rev4 panel quotes)',parts_unit_assumptions=unit,parts_quantities_per_panel=qty,parts_per_five_panels_usd=parts,bare_five_panels_budget_usd=bare,joints_per_panel=joints,smt_5panels_usd=smt,public_rate_inputs=fees,rows=rows,manual_batch_hours=manualtime,manual_labor_usd_per_hour=labor,manual_owned_tools_with_valued_labor_usd=[kit_owned[i]+manualtime[i]*labor[i] for i in (0,1)],manual_new_kit_with_valued_labor_usd=[kit_new[i]+manualtime[i]*labor[i] for i in (0,1)],kit_oneoff_increment_usd=[40,120],stencil_budget_usd=[10,20],consumables_batch_usd=[10,25],excluded='freight, import/tax, stock/MOQ/attrition, keyboard surcharge, PCB/PCBA DFM revisions, case, switches, plate, Main, harness, training, failed boards; no live BOM reservation')
(E/'costs.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(rows,indent=2))
