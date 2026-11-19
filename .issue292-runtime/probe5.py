import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
t = b.GetTracks()[0]
print([m for m in dir(t) if 'uid' in m.lower() or 'UID' in m])
try: print('GetUUID:', t.GetUUID())
except Exception as e: print('GetUUID err', e)
try: print('m_Uuid:', t.m_Uuid, t.m_Uuid.AsString())
except Exception as e: print('m_Uuid err', e)
