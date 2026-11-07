"""Rev4 explicit source contract, derived from the pre-router #175 logical circuit."""
from common import *
source=E.parent/'issue-175-main-dual-wing-final2/logical-contract.json'
components=json.loads(source.read_text())['components']
for ref in ['J1','R1','R2','U2']:del components[ref]
components['J4']=dict(value='SM04B-SRSS-TB(LF)(SN)',pins={'1':'VBUS','2':'USB_DM_ESD','3':'USB_DP_ESD','4':'GND'},pin_roles={},source='Phase A-2 UDB C3 1:1 connector contract')
assert len(components)==59
save(E/'logical-contract.json',dict(basis_sha256=digest(source),components=components,removed=['J1','R1','R2','U2'],added=['J4']))
