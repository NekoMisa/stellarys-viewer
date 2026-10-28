"""Check Firestorm semantic colours and group layout in Midnight (no viewer launch)."""
from pathlib import Path
import argparse
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--payload', type=Path)
args = parser.parse_args()
skins = Path(__file__).resolve().parents[2] / 'indra/newview/skins'
def palette(*files):
    result = {}
    for file in files:
        result.update({e.attrib['name']: e.attrib for e in ET.parse(file).getroot()})
    return result

def value(table, name):
    visited = set()
    while 'reference' in table[name]:
        assert name not in visited, 'Colour reference cycle'
        visited.add(name)
        name = table[name]['reference']
    return tuple(map(float, table[name]['value'].split()))

firestorm = palette(skins/'default/colors.xml', skins/'firestorm/colors.xml')
midnight = palette(skins/'default/colors.xml', skins/'stellarys_midnight/colors.xml')
roles = [n for n in firestorm if n.startswith(('AvatarListItem', 'MapAvatar')) or n == 'UserChatColor']
for role in roles:
    assert value(midnight, role) == value(firestorm, role), role
assert value(midnight, 'MapAvatarColor') == value(firestorm, 'Green')
assert value(midnight, 'MapAvatarFriendColor') == value(firestorm, 'Yellow')
assert value(midnight, 'UserChatColor') == (1, 1, 1, 1)
assert value(midnight, 'AccentColor') != value(firestorm, 'AccentColor')
assert value(midnight, 'SL-Background_66') != value(firestorm, 'SL-Background_66')
group = Path('xui/en/panel_group_info_sidetray.xml')
assert (skins/'stellarys_midnight'/group).read_bytes() == (skins/'firestorm'/group).read_bytes()
ET.parse(skins/'stellarys_midnight'/group)
if args.payload:
    for source in (skins/'stellarys_midnight').rglob('*'):
        if source.is_file():
            assert source.read_bytes() == (args.payload/'skins/stellarys_midnight'/source.relative_to(skins/'stellarys_midnight')).read_bytes(), source.name
print('PASS:', len(roles), 'Firestorm radar/minimap/chat colour roles, complete group layout and Midnight palette; payload checked:', bool(args.payload))
