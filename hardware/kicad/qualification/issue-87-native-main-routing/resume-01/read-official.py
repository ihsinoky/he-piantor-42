from session import *
for path in ['src/main/java/app/freerouting/designforms/specctra/Structure.java','src/main/java/app/freerouting/designforms/specctra/DsnFile.java','src/main/java/app/freerouting/designforms/specctra/Network.java','src/main/java/app/freerouting/interactive/HeadlessBoardManager.java','src/main/java/app/freerouting/rules/BoardRules.java','src/main/java/app/freerouting/rules/ClearanceMatrix.java','src/main/java/app/freerouting/settings/RouterOptimizerSettings.java','src/main/java/app/freerouting/designforms/specctra/CoordinateTransform.java']:
    dest=ROOT/'evidence/official'/Path(path).name
    dest.parent.mkdir(exist_ok=True)
    run('source-'+Path(path).stem,['curl','-fL','https://raw.githubusercontent.com/freerouting/freerouting/v2.1.0/'+path,'-o',str(dest)],BASE,120)
