import pcbnew as p
from pathlib import Path
path=Path('/tmp/eda004e/settings-probe');path.mkdir()
m=p.GetSettingsManager();print('manager',m)
print('load',m.LoadProject(str(path/'probe.kicad_pro')))
b=p.BOARD();b.SetProject(m.Prj());s=b.GetDesignSettings()
print('netsettings',s.m_NetSettings)
n=s.m_NetSettings.GetDefaultNetclass();print('default',n.GetClearance(),n.GetTrackWidth())
s.m_MinClearance=p.FromMM(.2);s.m_TrackMinWidth=p.FromMM(.2)
n.SetClearance(p.FromMM(.2));n.SetTrackWidth(p.FromMM(.2));n.SetViaDiameter(p.FromMM(.6));n.SetViaDrill(p.FromMM(.3))
b.SetFileName(str(path/'probe.kicad_pcb'));print('saveboard',p.SaveBoard(str(path/'probe.kicad_pcb'),b));print('saveproject',m.SaveProject(str(path/'probe.kicad_pro')))
print('files',list(path.iterdir()))
