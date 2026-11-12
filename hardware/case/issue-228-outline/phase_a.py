"""2D-only PO gate; never imports the CAD generator or produces 3D geometry."""
from pathlib import Path
import csv
import hashlib
import json
import math
import os
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / '.issue228-runtime'
os.environ.setdefault('MPLCONFIGDIR', str(RUNTIME / 'mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union, nearest_points
from outline import proposed_outline, wing_envelope


def vertices(g):
    # Remove exact collinear splits from Boolean operations, not shape corners.
    return len(g.simplify(1e-8, preserve_topology=True).exterior.coords)-1


def distance_record(a, b):
    p, q = nearest_points(a, b)
    return dict(mm=a.distance(b), first_xy=list(p.coords[0]), second_xy=list(q.coords[0]))


def main():
    source = ROOT / 'hardware/case/issue-198-final/17mm/dimensions.json'
    data = json.loads(source.read_text())
    boards = {k: Polygon(v) for k, v in data['boards'].items()}
    # Independently rebuild unchanged Wing boundaries from the authoritative CSVs.
    for side in ('left', 'right'):
        t = data['wing_transforms'][side]
        path = source.parent.parent / f'inputs/rev3-final/outline-17mm-{side}.csv'
        with path.open() as f:
            points = [[float(r['x_mm']), float(r['y_mm'])] for r in csv.DictReader(f)]
        transformed = Polygon([[sum(t['matrix'][i][j]*p[j] for j in range(2)) + t['translation'][i] for i in range(2)] for p in points])
        assert transformed.equals_exact(boards['wing_'+side], 1e-9)
    # Same extraction arithmetic and tolerance as base.generate, no pocket edits.
    cavity = unary_union([g.buffer(.502, join_style=2) for g in boards.values()] + [box(-11,-24,11,12)]).simplify(.002, preserve_topology=True)
    old = cavity.buffer(2., join_style=2)
    new = proposed_outline(cavity, boards)
    # details.finish adds these unchanged floor-only splice reinforcements.
    plates = [box(-10.5,y-8,17.5,y+8) for y in (-8.,55.)]
    old_final, new_final = [unary_union([g,*plates]) for g in (old,new)]
    assert new_final.buffer(1e-8).covers(old_final)
    assert new_final.covers(cavity)
    wall = distance_record(cavity.boundary, new.boundary)
    assert wall['mm'] >= 2.-1e-8
    measures = dict(pitch_mm=17, coordinates='assembly XY mm; +Y south',
                    source_dimensions_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                    pocket_outside_proposal_mm2=cavity.difference(new).area,
                    legacy_outline_outside_proposal_mm2=old_final.difference(new_final).area,
                    wall_minimum=wall, trays={}, wings={})
    for side, clip in [('left',box(-300,-200,3.5,200)),('right',box(3.5,-200,300,200))]:
        before, after = [g.intersection(clip) for g in (old_final,new_final)]
        b=after.bounds
        measures['trays'][side] = dict(vertices_before=vertices(before), vertices_after=vertices(after),
            raw_vertices_before=len(before.exterior.coords)-1, raw_vertices_after=len(after.exterior.coords)-1,
            bounds_xy_mm=list(b), footprint_xy_mm=[b[2]-b[0],b[3]-b[1]],
            with_5mm_brim_xy_mm=[b[2]-b[0]+10,b[3]-b[1]+10])
        assert max(measures['trays'][side]['with_5mm_brim_xy_mm']) <= 220
        pcb=boards['wing_'+side]; clear=pcb.buffer(.502,join_style=2)
        envelope, line=wing_envelope(pcb)
        assert new.covers(clear)
        south_segment = LineString(line['endpoints'])
        # Require the whole run to be exposed boundary, with no residual steps.
        assert south_segment.difference(new.boundary.buffer(1e-8)).length < 1e-8
        measures['wings'][side]=dict(south_line=line,
            pcb_margin=distance_record(pcb.boundary,new.boundary),
            clearance_margin=distance_record(clear.boundary,new.boundary),
            clearance_outside_mm2=clear.difference(new).area,
            clearance_covered=new.covers(clear))
    measures['total_vertices_before']=sum(t['vertices_before'] for t in measures['trays'].values())
    measures['total_vertices_after']=sum(t['vertices_after'] for t in measures['trays'].values())
    # Continuous polygon operations, not a sample-point containment check.
    # Save the exact generator-consumable proposal as 2D evidence.
    (HERE/'17mm-outline.json').write_text(json.dumps(dict(measurements=measures,
        cavity_xy=list(cavity.exterior.coords),current_xy=list(old_final.exterior.coords),
        proposed_xy=list(new_final.exterior.coords)),indent=2)+'\n')
    (RUNTIME/'measurements.json').write_text(json.dumps(measures,indent=2)+'\n')
    def draw(ax, g, **kw):
        x,y=g.exterior.xy;ax.plot(x,y,**kw)
    def plot(ax, zoom=False):
        for k,g in boards.items():
            ax.fill(*g.exterior.xy,color='#d9e5ee',alpha=.85)
        draw(ax,cavity,color='#748596',lw=.75,label='Unchanged pocket (+0.502 mm)')
        draw(ax,old_final,color='#d65343',lw=1.6,ls='--',label='Current Issue #198')
        draw(ax,new_final,color='#007c83',lw=2,label='Proposed Issue #228')
        ax.axvline(3.5,color='#5e4b95',ls=':',lw=1,label='Split X = 3.5 mm')
        ax.set_aspect('equal');ax.invert_yaxis();ax.grid(alpha=.15)
        ax.set_xlabel('Assembly X (mm)');ax.set_ylabel('Assembly Y (mm; south downward)')
        if zoom:
            ax.set_xlim(-153,-37);ax.set_ylim(91,-10)
            line=measures['wings']['left']['south_line']
            a,b=line['endpoints'];mid=[(a[i]+b[i])/2 for i in range(2)]
            ax.annotate(f"One straight south edge: {line['length_mm']:.2f} mm",xy=mid,xytext=(-112,81),
                arrowprops=dict(arrowstyle='->',color='#007c83'),color='#005e63',fontsize=10)
            ax.text(-147,-5,'Pinky',fontsize=11);ax.text(-62,88,'Thumb',fontsize=11)
        else:
            ax.set_xlim(-158,158);ax.set_ylim(98,-78)
        ax.legend(loc='upper right',fontsize=8,framealpha=.95)
    fig,ax=plt.subplots(figsize=(14,8));plot(ax)
    ax.set_title('Issue #228 • 17 mm • assembled trays • 2D outline approval proposal')
    fig.tight_layout();fig.savefig(HERE/'17mm-outline-overlay.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,8));plot(ax,True)
    ax.set_title('Left south edge detail • right wing mirrored • PCB/pocket unchanged')
    fig.tight_layout();fig.savefig(HERE/'17mm-south-edge-zoom.png',dpi=180);plt.close(fig)
    print(json.dumps(measures,indent=2))


if __name__ == '__main__':
    main()
