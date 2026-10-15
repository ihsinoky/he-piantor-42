from session import *
classes=BASE/'inspector';classes.mkdir(exist_ok=True)
run('compile-public-inspector',[str(JAVA.with_name('javac')),'-cp',str(JAR),'-d',str(classes),str(ROOT/'InspectDsn.java')],BASE)
for name in ['smoke','main']:
    for version in ['raw','corrected']:
        input=Path('/tmp/issue87')/name/'input.dsn' if version=='raw' else BASE/name/'corrected.dsn'
        out=BASE/name/(version+'-effective.json')
        run(name+'-read-'+version,[str(JAVA),'-Djava.awt.headless=true','-cp',str(JAR)+':'+str(classes),'InspectDsn',str(input),str(out)],BASE,60,artifacts=[('effective.json',out)])
