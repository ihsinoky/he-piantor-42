# Issue #303 Stage 1 — plan

1. Read inputs: Issue #303, centre study §7, D-048/059/060 (D-062 via issue text; not on main).
2. Derive series topology from contact geometry (alternating cell orientation):
   C1(+N/−S), C2(−N/+S), C3(+N/−S) → bridge B1 north (C1+–C2−), bridge B2 south (C2+–C3−),
   return pour east edge (C3+ NE → south exit), PACK− = C1− SW. Proof table in design note.
3. Availability scan: Keystone 209-class contacts, Littelfuse 1206L050/24WR PTC,
   SS-12D10-class switch, JST BM02B-GHS-TBT + GHR-02V-S cable parts.
4. Build KiCad schematic (project-local symbols), ERC via kicad-cli, fix to 0.
5. Design note + Draft PR + Issue comment + GOAL.md line. NO layout.
