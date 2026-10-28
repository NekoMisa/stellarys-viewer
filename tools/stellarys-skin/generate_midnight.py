"""Generate Stellarys Midnight's original UI primitives (requires Pillow).

No existing artwork, application settings or other skins are modified.
Coordinates for the viewer's nine-slice textures are measured from bottom-left.
Copyright (c) 2026 NekoMisa. SPDX-License-Identifier: LGPL-2.1-only
"""
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2] / 'indra/newview/skins'
SKIN = ROOT / 'stellarys_midnight'
TEX = SKIN / 'textures'
TEX.mkdir(parents=True, exist_ok=True)
COLORS = {
    'base': '#070d1c', 'panel': '#0c162b', 'raised': '#14213b',
    'line': '#2b3b58', 'text': '#e7edf8', 'muted': '#adbcd3',
    'accent': '#ad9bfa', 'selected': '#303253', 'hover': '#202f4c',
    'disabled': '#78879e',
    'unread': '#355574', 'mention': '#466583',
}

def xml_write(root, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space='  ')
    ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)
    with path.open('a', encoding='utf-8') as stream:
        stream.write('\n')

def rgba(value, alpha=1):
    return ' '.join(f'{int(value[i:i+2], 16)/255:.6f}' for i in (1, 3, 5)) + f' {alpha:g}'

colors = ET.Element('colors')
for name, value in COLORS.items():
    ET.SubElement(colors, 'color', name='Stellarys' + name.title(), value=rgba(value))

roles = {
    'base': ['DkGrayLogin', 'PanelDark', 'TextBgFocusColor', 'TextBgWriteableColor',
             'TextBgReadOnlyColor', 'FilterBackgroundColor', 'ScrollBgWriteableColor',
             'ScrollBgReadOnlyColor', 'BackgroundChatColor', 'FSChatHistoryBackground',
             'ChatHeaderOpaqueBackground'],
    'panel': ['DkGray', 'DkGray2', 'PanelGray', 'SL-Background', 'SL-Background_Light',
              'PanelDefaultBackgroundColor', 'PanelFocusBackgroundColor',
              'MenuBarBgColor', 'MenuDefaultBgColor', 'MenuPopupBgColor',
              'ComboListBgColor', 'ToolTipBgColor', 'UploadDialogBackground',
              'PieMenuBgColor', 'PieMenuBgColorOverride'],
    'raised': ['MouseGray', 'ScrollBGStripeColor'],
    'text': ['TextFgColor', 'TextFgReadOnlyColor', 'TextDefaultColor',
             'TextCursorColor', 'LabelTextColor', 'LabelSelectedColor',
             'ButtonLabelColor', 'ButtonLabelSelectedColor', 'MenuItemEnabledColor',
             'MenuItemHighlightFgColor', 'ScrollSelectedFGColor', 'ScrollUnselectedColor',
             'InventoryItemEnabledColor', 'InventoryItemLibraryColor',
             'InventoryItemHighlightFgColor', 'AccordionHeaderTextColor',
             'ToolTipTextColor', 'PieMenuTextColor', 'ScriptDialogFg'],
    'muted': ['TextFgTentativeColor', 'InventoryItemLinkColor', 'InventoryItemSuffixColor'],
    'disabled': ['LabelDisabledColor', 'LabelSelectedDisabledColor',
                 'ButtonLabelDisabledColor', 'ButtonLabelSelectedDisabledColor',
                 'MenuItemDisabledColor', 'ScrollDisabledColor'],
    'selected': ['SchemeDark', 'MenuItemHighlightBgColor',
                 'ScrollSelectedBGColor', 'InventoryItemHighlightBgColor',
                 'TextBgHighlightColor', 'SelectedBgReadOnlyColor',
                 'PieMenuSelectedColor', 'PieMenuSelectedColorOverride'],
    'accent': ['AccentColor', 'EmphasisColor', 'EmphasisColorLight', 'SchemeLightest',
               'FocusColor', 'ColorSwatchBorderColor', 'HintTitle', 'HTMLLinkColor', 'HTMLLinkColorHovertips'],
    'hover': ['ScrollHoveredColor', 'InventoryMouseOverColor'],
    'line': ['FloaterFocusBorderColor', 'FloaterUnfocusBorderColor',
             'ResizebarBorderLight', 'ResizebarBorderDark', 'ToolTipBorderColor'],
    # Notification colours only: keep the existing flash timing/count/settings.
    # The base palette points unread highlights at its neon diagnostic colour.
    'unread': ['ButtonFlashBgColor'],
    'mention': ['MentionFlashBgColor'],
}
for palette, names in roles.items():
    for name in names:
        ET.SubElement(colors, 'color', name=name, reference='Stellarys' + palette.title())
for name, palette, alpha in [
    ('EmphasisColor_13', 'accent', .13), ('EmphasisColor_35', 'accent', .35),
    ('SchemeLightest_35', 'accent', .35), ('DkGray_66', 'panel', .90),
    ('DkGray_86', 'panel', .96), ('SL-Background_50', 'panel', .5),
    ('SL-Background_66', 'panel', .9), ('FloaterDefaultBackgroundColor', 'panel', .96),
    ('FloaterFocusBackgroundColor', 'panel', 1), ('TitleBarFocusColor', 'accent', .035),
    ('ScriptDialog', 'raised', 1), ('ChatHeaderAlphaBackground', 'panel', .9),
]:
    ET.SubElement(colors, 'color', name=name, value=rgba(COLORS[palette], alpha))
# Radar and minimap meaning colours follow Firestorm, independently of Midnight's accent.
# Resolve references before copying so AvatarListItemChatRange does not inherit
# our violet AccentColor. Saved per-user/contact-set choices remain untouched.
firestorm_colors = {}
for palette_file in (ROOT/'default/colors.xml', ROOT/'firestorm/colors.xml'):
    firestorm_colors.update({entry.get('name'): entry.attrib for entry in ET.parse(palette_file).getroot()})
def firestorm_color_value(name, seen=()):
    if name in seen:
        raise ValueError('Colour reference cycle: ' + name)
    entry = firestorm_colors[name]
    return entry['value'] if 'value' in entry else firestorm_color_value(entry['reference'], seen + (name,))
for name in sorted(firestorm_colors):
    if name.startswith(('AvatarListItem', 'MapAvatar')) or name == 'UserChatColor':
        ET.SubElement(colors, 'color', name=name, value=firestorm_color_value(name))
xml_write(colors, SKIN / 'colors.xml')

textures = ET.Element('textures', version='101')
SCALE = 4

def primitive(filename, size, fill, outline=None, radius=4, decorate=None):
    """Draw new vector-like UI geometry at 4x, then rasterize for the viewer."""
    w, h = size
    image = Image.new('RGBA', (w*SCALE, h*SCALE))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1, 1, w*SCALE-2, h*SCALE-2), radius=radius*SCALE,
                           fill=fill, outline=outline, width=SCALE if outline else 1)
    if decorate:
        decorate(draw, w, h)
    image = image.resize(size, Image.Resampling.LANCZOS)
    image.save(TEX / (filename + '.png'), optimize=True)

def texture(name, filename, size=None, borders=(5,5,5,5)):
    attrs = {'name': name, 'file_name': filename + '.png', 'preload': 'true'}
    if size:
        w, h = size
        left, top, right, bottom = borders
        attrs.update({'scale.left':str(left), 'scale.top':str(h-top),
                      'scale.right':str(w-right), 'scale.bottom':str(bottom)})
    ET.SubElement(textures, 'texture', attrs)

states = {
    'off': ('raised', 'line'), 'hover': ('hover','muted'),
    'selected': ('selected','accent'), 'pressed': ('selected','text'),
    'disabled': ('panel','line'), 'selected_disabled': ('raised','line'),
}
for state, (fill, border) in states.items():
    primitive('button_' + state, (64,24), COLORS[fill], COLORS[border])
    primitive('tab_' + state, (64,24), COLORS[fill], None, radius=2,
              decorate=(lambda d,w,h: d.rectangle((4*SCALE,(h-2)*SCALE,(w-4)*SCALE,(h-1)*SCALE),fill=COLORS['accent']))
              if state in ('selected','pressed') else None)
for entry in ET.parse(ROOT/'default/textures/textures.xml').getroot():
    name = entry.get('name','')
    if name.startswith(('PushButton_', 'SegmentedBtn_', 'Toolbar_', 'TabTop_')):
        if not name.startswith(('PushButton_', 'SegmentedBtn_', 'TabTop_')) and not any(p in name for p in ('Left_', 'Middle_', 'Right_')):
            continue
        state = 'off'
        if 'Disabled' in name: state = 'selected_disabled' if 'Selected' in name else 'disabled'
        elif any(p in name for p in ('Press','Flashing','Flash')): state = 'pressed'
        elif 'Selected' in name or name in ('PushButton_On',): state = 'selected'
        elif 'Over' in name: state = 'hover'
        elif any(p in name for p in ('Login','Sign')): state = 'selected'
        texture(name, ('tab_' if name.startswith('TabTop_') else 'button_') + state, (64,24))

# Retain the familiar category-specific folder artwork. Without these aliases,
# the base skin substitutes the same generic system-folder icon for most types.
# The legacy artwork is already bundled in default/textures: do not duplicate it
# or recolour its semantic details (animation, clothing, sound, landmark, etc.).
for entry in ET.parse(ROOT/'firestorm/textures/textures.xml').getroot():
    name=entry.get('name','')
    if name.startswith('Inv_') and name.endswith(('Open','Closed')):
        assert (ROOT/'default/textures'/entry.get('file_name')).is_file(),name
        ET.SubElement(textures,'texture',dict(entry.attrib))

def inbox_arrow(draw,w,h,expanded=False):
    points=[(14,15),(24,15),(19,21)] if expanded else [(16,11),(23,17),(16,23)]
    draw.polygon([(x*SCALE,y*SCALE) for x,y in points],fill=COLORS['text' if expanded else 'muted'])

# This bar has its own baked-in arrow and never uses the generic button images.
# Preserve its native 40x35 dimensions and fixed 30px arrow/label padding region.
for state in ('off','selected'):
    primitive('marketplace_'+state,(40,35),COLORS['raised' if state=='off' else 'selected'],
              COLORS['line' if state=='off' else 'accent'],radius=4,
              decorate=lambda d,w,h,s=state:inbox_arrow(d,w,h,s=='selected'))
    texture('MarketplaceBtn_'+('Off' if state=='off' else 'Selected'),
            'marketplace_'+state,(40,35),(30,16,5,4))

def window_title(draw, w, h, active=True):
    draw.rectangle((SCALE, 7*SCALE, (w-1)*SCALE, 24*SCALE), fill=COLORS['raised'] if active else COLORS['panel'])
    draw.line((SCALE,24*SCALE,(w-1)*SCALE,24*SCALE), fill=COLORS['line'], width=SCALE)
    # Sparse blue-white constellations stay inside fixed nine-slice corners.
    # They never stretch into streaks or appear behind the window's controls.
    for x,y,r in [(5,6,1.0),(7,14,2.0),(4,21,.7),
                  (w-7,6,.8),(w-5,15,2.1),(w-8,22,.8)]:
        x*=SCALE;y*=SCALE;r*=SCALE
        draw.polygon([(x,y-r),(x+r*.3,y-r*.3),(x+r,y),(x+r*.3,y+r*.3),
                      (x,y+r),(x-r*.3,y+r*.3),(x-r,y),(x-r*.3,y-r*.3)],
                      fill='#c7e0fa' if active else '#91aacb')
for state in ('active','inactive'):
    primitive('window_'+state,(128,64),COLORS['panel'],COLORS['line'],radius=6,
              decorate=lambda d,w,h,s=state:window_title(d,w,h,s=='active'))
texture('Window_Foreground','window_active',(128,64),(10,25,10,6))
texture('Window_Background','window_inactive',(128,64),(10,25,10,6))
primitive('surface',(64,32),COLORS['panel'],COLORS['line'],radius=5)
for name in ('Window_NoTitle_Foreground','Window_NoTitle_Background','Toast_Background','Toast_Over','Tooltip'):
    texture(name,'surface',(64,32),(6,6,6,6))
primitive('white_rounded',(64,32),'white',radius=5)
texture('Rounded_Rect','white_rounded',(64,32),(6,6,6,6))

for state in ('off','active','disabled'):
    primitive('field_'+state,(64,24),COLORS['base'],COLORS['accent' if state=='active' else 'line'],radius=4)
for suffix in ('Off','Search_Off','Active','Search_Active','Highlight','Search_Highlight','Disabled','Search_Disabled'):
    state='disabled' if 'Disabled' in suffix else 'active' if any(s in suffix for s in ('Active','Highlight')) else 'off'
    texture('TextField_'+suffix,'field_'+state,(64,24))

def arrow(draw,w,h,up=False):
    cx=(w-12)*SCALE;cy=h/2*SCALE;sign=-1 if up else 1
    draw.line([(cx-3*SCALE,cy-sign*SCALE),(cx,cy+sign*2*SCALE),(cx+3*SCALE,cy-sign*SCALE)],fill=COLORS['text'],width=SCALE)
for state in ('off','selected','disabled'):
    primitive('dropdown_'+state,(122,23),COLORS['base'],COLORS['accent' if state=='selected' else 'line'],decorate=arrow)
    primitive('combo_'+state,(22,23),COLORS['base'],COLORS['accent' if state=='selected' else 'line'],decorate=arrow)
for name in ('DropDown_Off','DropDown_On','DropDown_Press','DropDown_Disabled'):
    state='disabled' if 'Disabled' in name else 'selected' if any(s in name for s in ('On','Selected','Press')) else 'off'
    texture(name,'dropdown_'+state,(122,23),(5,5,23,5))
# LLComboBox sizes editable combos from the arrow image's intrinsic width.
# Preserve the native 22px width; sharing the full field image makes it huge.
for name in ('ComboButton_Off','ComboButton_Selected','ComboButton_On','ComboButton_Disabled'):
    state='disabled' if 'Disabled' in name else 'selected' if any(s in name for s in ('On','Selected')) else 'off'
    texture(name,'combo_'+state,(22,23),(4,4,4,4))

def tick(draw,w,h):
    draw.line([(3*SCALE,6*SCALE),(5*SCALE,9*SCALE),(10*SCALE,3*SCALE)],fill=COLORS['text'],width=2*SCALE)
for state in ('off','on','disabled','on_disabled'):
    primitive('check_'+state,(13,13),COLORS['selected'] if state=='on' else COLORS['base'],
              COLORS['accent'] if state=='on' else COLORS['line'],radius=2,
              decorate=tick if state.startswith('on') else None)
for name in ('Checkbox_Off','Checkbox_Slim_Off','Checkbox_On','Checkbox_Slim_On',
             'Checkbox_Off_Disabled','Checkbox_On_Disabled','Checkbox_Press','Checkbox_On_Press'):
    state='on' if '_On' in name else 'off'
    if 'Disabled' in name:state='on_disabled' if state=='on' else 'disabled'
    texture(name,'check_'+state)

for direction,size in [('vertical',(12,32)),('horizontal',(32,12))]:
    primitive('scroll_'+direction,size,COLORS['line'],radius=5)
    primitive('track_'+direction,size,COLORS['base'],radius=0)
    name='Vert' if direction=='vertical' else 'Horiz'
    texture('ScrollThumb_'+name,'scroll_'+direction,size,(4,4,4,4))
    texture('ScrollTrack_'+name,'track_'+direction,size,(2,2,2,2))
for direction,size in [('Horiz',(32,6)),('Vert',(6,32))]:
    primitive('slider_'+direction,size,COLORS['line'],radius=2)
    texture('SliderTrack_'+direction,'slider_'+direction,size,(2,2,2,2))
for state,palette in [('Off','accent'),('Press','text'),('Disabled','disabled')]:
    primitive('thumb_'+state,(14,14),COLORS[palette],radius=7)
    texture('SliderThumb_'+state,'thumb_'+state)

for name,palette in [('panel','panel'),('base','base'),('progress','accent')]:
    primitive('flat_'+name,(16,16),COLORS[palette],radius=0)
for name in ('NavBar_BG','NavBar_BG_NoFav_Bevel','NavBar_BG_NoNav_Bevel'):
    texture(name,'flat_panel',(16,16),(1,1,1,1))
for name in ('ProgressBar','ProgressBarSolid'):
    texture(name,'flat_progress',(16,16),(1,1,1,1))
texture('ProgressTrack','flat_base',(16,16),(1,1,1,1))
for name in ('Accordion_Off','Accordion_Over','Accordion_Press','Accordion_Selected'):
    state='selected' if name.endswith(('Press','Selected')) else 'hover' if name.endswith('Over') else 'off'
    texture(name,'button_'+state,(64,24))
xml_write(textures,TEX/'textures.xml')
# Skin XUI files replace their fallback wholesale. Retain every base parameter
# and nested control, then change style.
# Sparse files here would remove button images, window chrome and scrollbars.
widget_changes = {
    'floater.xml': {'bg_opaque_color':'White', 'bg_alpha_color':'White',
                    'header_font_shadow':'none'},
    'button.xml': {'hover_glow_amount':'0.12', 'label_shadow':'false'},
    # drawSolid uses the alpha mask, so supply the track colour explicitly.
    'scroll_bar.xml': {'track_color':'StellarysBase', 'thumb_color':'White'},
    'line_editor.xml': {'highlight_color':'StellarysSelected', 'preedit_bg_color':'StellarysBase'},
    'simple_text_editor.xml': {'bg_selected_color':'StellarysSelected'},
    'toolbar.xml': {},
}
for name, attrs in widget_changes.items():
    widget = ET.parse(ROOT/'default/xui/en/widgets'/name).getroot()
    widget.attrib.update(attrs)
    if name == 'toolbar.xml':
        widget.find('button_panel').set('bg_opaque_image_overlay','StellarysPanel')
    xml_write(widget,SKIN/'xui/en/widgets'/name)

# Skin lookup replaces whole panel files as well; preserve every control and
# callback while changing only the login panels' hardcoded grey background.
for name in ('panel_fs_login.xml','panel_fs_nui_login.xml'):
    panel=ET.parse(ROOT/'default/xui/en'/name).getroot()
    panel.set('bg_opaque_color','StellarysBase')
    xml_write(panel,SKIN/'xui/en'/name)

# Shared lookup lets Preferences show this palette before the user switches
# away from another skin. This is a style sample, not a logged-in screenshot.
preview = Image.new('RGB',(414,225),COLORS['base'])
draw = ImageDraw.Draw(preview)
font = ImageFont.load_default(size=16)
small = ImageFont.load_default(size=13)
draw.rounded_rectangle((8,8,405,216),radius=7,fill=COLORS['panel'],outline=COLORS['line'])
draw.rounded_rectangle((9,9,404,40),radius=6,fill=COLORS['raised'])
draw.text((22,17),'Stellarys Midnight',font=font,fill=COLORS['text'])
draw.text((22,56),'Deep midnight blue. A touch of starlight.',font=small,fill=COLORS['muted'])
for index,(text,state) in enumerate([('Camera','selected'),('Shot presets','off'),('Paths','off')]):
    x=22+index*123
    draw.rounded_rectangle((x,88,x+111,116),radius=4,fill=COLORS[states[state][0]],outline=COLORS[states[state][1]])
    draw.text((x+9,94),text,font=small,fill=COLORS['text'])
draw.rounded_rectangle((22,136,390,163),radius=4,fill=COLORS['base'],outline=COLORS['line'])
draw.text((33,142),'A quieter space for your next shot.',font=small,fill=COLORS['muted'])
draw.text((22,186),'Skin colour sample',font=small,fill=COLORS['muted'])
for x,y,r in [(374,18,1),(385,27,2),(396,16,1),(15,184,1),(398,193,2)]:
    draw.line((x-r,y,x+r,y),fill='#c7e0fa')
    draw.line((x,y-r,x,y+r),fill='#c7e0fa')
preview_path=ROOT/'default/textures/skinspreview/stellarys_midnight.png'
preview_path.parent.mkdir(parents=True,exist_ok=True)
preview.save(preview_path,optimize=True)
shutil.copyfile(ROOT/'default/html/en-us/stellarys/privacy.html',
                SKIN/'html/en-us/stellarys/privacy.html')
# Keep Firestorm's complete group profile layout; shared Midnight colour roles
# and widget defaults still supply its appearance.
shutil.copyfile(ROOT/'firestorm/xui/en/panel_group_info_sidetray.xml',
                SKIN/'xui/en/panel_group_info_sidetray.xml')
print('Generated',len(list(TEX.glob('*.png'))),'original UI textures and',len(textures),'texture aliases.')
