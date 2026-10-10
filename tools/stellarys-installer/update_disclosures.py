"""Regenerate the offline first-run text and HTML from the public policy documents."""
from pathlib import Path
import html, re

repo=Path(__file__).resolve().parents[2]
policy=(repo/'PRIVACY.md').read_text(encoding='utf-8')
disclosures=(repo/'DISCLOSURES.md').read_text(encoding='utf-8')
plain=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1: \2',disclosures+'\n\n'+policy)
plain=re.sub(r'^#+ ','',plain.replace('**','').replace('`',''),flags=re.M)
xui=repo/'indra/newview/skins/default/xui/en/floater_stellarys_disclosures.xml'
text=xui.read_text(encoding='utf-8')
start=text.index('>\n',text.index('<text_editor'))+2
end=text.index('\n </text_editor>',start)
xui.write_text(text[:start]+html.escape(plain)+text[end:],encoding='utf-8',newline='\n')
page=repo/'indra/newview/skins/default/html/en-us/stellarys/privacy.html'
text=page.read_text(encoding='utf-8')
start=text.index('<pre>')+5
end=text.index('</pre>',start)
page.write_text(text[:start]+html.escape(policy)+text[end:],encoding='utf-8',newline='\n')
print('Offline first-run disclosures and privacy HTML regenerated.')
