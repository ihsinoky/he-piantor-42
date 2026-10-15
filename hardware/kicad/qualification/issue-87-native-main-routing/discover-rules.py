from prepare import *
for name in ['pcbnew/specctra_import_export/specctra_export.cpp']:
    run('kicad-export-source',['curl','-fL','https://raw.githubusercontent.com/KiCad/kicad/9.0.9/'+name,'-o',str(ROOT/'evidence/specctra_export.cpp')],BASE,120)
for name in ['src/main/java/app/freerouting/designforms/specctra/RulesFile.java','src/main/java/app/freerouting/Freerouting.java','docs/settings.md']:
    out=ROOT/'evidence'/Path(name).name
    run('router-source-'+Path(name).stem,['curl','-fL','https://raw.githubusercontent.com/freerouting/freerouting/v2.1.0/'+name,'-o',str(out)],BASE,120)
