from prepare import *
run('parser-install',[str(BASE/'geometry/bin/pip'),'install','--require-hashes','-r',str(ROOT/'sexpdata-requirements.txt')],BASE,120)
