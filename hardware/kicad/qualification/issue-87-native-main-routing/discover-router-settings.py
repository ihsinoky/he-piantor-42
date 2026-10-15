from prepare import *
for name in ['src/main/java/app/freerouting/settings/GlobalSettings.java','src/main/java/app/freerouting/settings/RouterSettings.java','src/main/java/app/freerouting/core/RoutingJob.java','src/main/java/app/freerouting/core/RoutingJobScheduler.java']:
    out=ROOT/'evidence'/Path(name).name
    run('router-source-'+Path(name).stem,['curl','-fL','https://raw.githubusercontent.com/freerouting/freerouting/v2.1.0/'+name,'-o',str(out)],BASE,120)
