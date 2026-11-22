#!/usr/bin/env python3
"""Patch Stash's index.html so it runs on Safari 10 (iOS 10.3.x).
Usage: python patch_safari10.py index.html   -> writes index.safari10.html (original untouched)"""
import re, sys, pathlib

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'index.html')
s = src.read_text(encoding='utf-8')
if 'safari10-compat' in s:
    sys.exit('Already patched.')
miss = []

def rep(old, new):
    global s
    if old not in s: miss.append(old[:70]); return
    s = s.replace(old, new)

def rx(pat, new):
    global s
    s, n = re.subn(pat, lambda m: new, s)
    if not n: miss.append(pat[:70])

HEAD_JS = r"""<script>/* safari10-compat */(function(){var d=document.documentElement,c=[],ok=!1;try{ok=!!(window.CSS&&CSS.supports&&CSS.supports('padding','max(1px,2px)'))}catch(e){}
if(!ok)c.push('legacy');
try{var f=document.createElement('div');f.style.cssText='display:flex;flex-direction:column;gap:1px;position:absolute;visibility:hidden';f.innerHTML='<i style="display:block;height:1px"></i><i style="display:block;height:1px"></i>';d.appendChild(f);if(f.offsetHeight!==3)c.push('nfg');d.removeChild(f)}catch(e){if(!ok)c.push('nfg')}
d.className+=(d.className?' ':'')+c.join(' ')})();</script>
"""

PRE_CSS = """
dialog{width:calc(100vw - 24px);max-width:480px}
#toast{top:12px}
.fab{bottom:22px}
"""

POST_CSS = """
/* ---- Safari 10 / older WebKit fallbacks ---- */
.grid,.two{grid-gap:10px;grid-template-columns:minmax(0,1fr) minmax(0,1fr)}
.ico,.dot,.sg-face,input[type=checkbox]{justify-items:center;align-items:center}
.card::before{top:0;right:0;bottom:0;left:0}
.sg-face{top:0;left:0;width:100%;height:100%}
.k-eyes{top:9px;left:5px;right:5px;bottom:auto}
#stashley{top:0;left:0;z-index:60}
.top{position:-webkit-sticky;position:sticky}
#toast,.sg-bubble{width:-webkit-max-content}
li small,.sg-bubble,.hero .num{word-wrap:break-word}
dialog:not([open]){display:none}
dialog.poly[open]{display:block;position:fixed;z-index:41;left:50%;top:50%;margin:0;max-height:92vh;overflow:auto;-webkit-overflow-scrolling:touch;-webkit-transform:translate(-50%,-50%);transform:translate(-50%,-50%);animation:none}
.dlg-bd{position:fixed;top:0;right:0;bottom:0;left:0;z-index:40;background:rgba(37,21,53,.45)}
@media(max-width:520px){dialog.poly[open]{left:0;right:0;top:auto;bottom:0;width:100%;max-width:100%;max-height:90vh;-webkit-transform:none;transform:none;border-radius:26px 26px 0 0;animation:sheet .35s cubic-bezier(.2,.9,.3,1)}}
@media(max-width:340px){.hero .num{font-size:30px}.overview h2{font-size:24px}.top h1{font-size:23px}.overview-stats b{font-size:18px}}
.legacy .wrap{--px:16px}
.legacy .top{padding:12px var(--px);background:rgba(248,244,255,.96)}
.legacy .top,.legacy .card,.legacy .stat,.legacy li,.legacy .overview,.legacy .empty,.legacy .sg-bubble,.legacy dialog,.legacy .dlg-bd{-webkit-backdrop-filter:none;backdrop-filter:none}
.legacy body{background-attachment:scroll}
.nfg .row>*+*,.nfg li>*+*,.nfg .prev>*+*{margin-left:12px}
.nfg .top>*+*{margin-left:12px}
.nfg .top .r>*+*{margin-left:8px}
.nfg .tabs>*+*,.nfg .seg>*+*{margin-left:4px}
.nfg .btns>*+*,.nfg .chk>*+*{margin-left:8px}
.nfg .acts>*{margin:0 8px 8px 0}
.nfg .foot>*{margin:0 5px 10px}
.nfg .picker>*{margin:0 3px 6px}
.nfg .overview-stats>div{margin:0 20px 20px 0}
"""

POLY_JS = r"""
<script>/* dialog polyfill + helpers for browsers without <dialog> */
(function(){
var bd=null;
function ev(d,n){var e=document.createEvent('Event');e.initEvent(n,false,false);d.dispatchEvent(e)}
function hook(d){
 if(typeof d.showModal==='function')return;
 d.className+=' poly';
 Object.defineProperty(d,'open',{get:function(){return d.hasAttribute('open')},set:function(v){if(v)d.setAttribute('open','');else d.removeAttribute('open')}});
 d.showModal=function(){
  if(d.hasAttribute('open'))return;
  bd=document.createElement('div');bd.className='dlg-bd';document.body.appendChild(bd);
  d.setAttribute('open','');d.scrollTop=0;
 };
 d.close=function(){
  if(!d.hasAttribute('open'))return;
  d.removeAttribute('open');
  if(bd&&bd.parentNode)bd.parentNode.removeChild(bd);
  bd=null;ev(d,'close');
 };
}
var a=document.querySelectorAll('dialog');for(var i=0;i<a.length;i++)hook(a[i]);
document.addEventListener('keydown',function(e){if(e.key==='Escape'||e.keyCode===27){var o=document.querySelector('dialog.poly[open]');if(o)o.close()}});
window.ctv=function(){var c=document.querySelector('#cf input[name=ct]:checked');return c?c.value:'add'};
if(/(^|\s)legacy(\s|$)/.test(document.documentElement.className)){var b=document.getElementById('acct');if(b){b.className=b.className.replace('hide','');b.textContent='On this device';b.disabled=true}}
})();
</script>"""

# ---- JS syntax Safari 10 can't parse ----
rx(r'catch\s*\{', 'catch(_e){')                       # optional catch binding
rx(r'g\.icon\?\.', '(g.icon||{}).')                   # optional chaining
rx(r'g\.remind\?\.', '(g.remind||{}).')
rep("if(!bag?.length){", "if(!(bag&&bag.length)){")
rep("String(s??'')", "String(s==null?'':s)")           # nullish coalescing
rep("v[k]??''", "(v[k]==null?'':v[k])")
rep("const W=52;", "const W=52;const vvh=()=>window.visualViewport?window.visualViewport.height:innerHeight;")
rep("window.visualViewport?.height||innerHeight", "vvh()")
rep("window.visualViewport?.addEventListener('resize',reposition);",
    "if(window.visualViewport)window.visualViewport.addEventListener('resize',reposition);")
rep("{...g.icon}", "Object.assign({},g.icon)")          # object spread
rep("icon:{...draft}", "icon:Object.assign({},draft)")
rep("{id:nextId(),logs:[],...o}", "Object.assign({id:nextId(),logs:[]},o)")
rep("{...v,m:ms}", "Object.assign({},v,{m:ms})")
rep("[...el.querySelectorAll('.sg-face')]", "Array.prototype.slice.call(el.querySelectorAll('.sg-face'))")

# ---- APIs that behave differently / are missing ----
rep("const fdate=d=>new Date(d+'T00:00').toLocaleDateString",
    "const pd=(v,end)=>{const p=v.split('-');return end?new Date(+p[0],+p[1]-1,+p[2],23,59,59):new Date(+p[0],+p[1]-1,+p[2])};\nconst fdate=d=>pd(d).toLocaleDateString")
rep("(new Date(g.date+'T23:59:59')-new Date())", "(pd(g.date,1)-new Date())")
rep("new Date(g.date+'T23:59:59').getTime()", "pd(g.date,1).getTime()")
rep("Date.parse(today()+'T00:00')-Date.parse(la.date+'T00:00')", "pd(today()).getTime()-pd(la.date).getTime()")
rep("$('#cf').ct.value='add'", "(document.querySelector('#cf input[value=add]').checked=true)")
rep("$('#cf').ct.value", "ctv()")
rep("🪙", "💵")                                          # emoji too new for iOS 10
rep("else if(a==='exp'){const b=new Blob",
    "else if(a==='exp'){if(!('download' in document.createElement('a'))){window.open('data:text/plain;charset=utf-8,'+encodeURIComponent(JSON.stringify(S)));return}const b=new Blob")
rep("if(RM()||document.hidden){setPos(x1,y1);flying=false;return res()}",
    "if(RM()||document.hidden){setPos(x1,y1);flying=false;return res()}\n    if(!el.animate){const ms=Math.min(1500,Math.max(700,500+dist*.8));el.style.transition='transform '+ms+'ms ease-in-out';setPos(x1,y1);setTimeout(()=>{el.style.transition='';res()},ms);return}")
rx(r'function confetti\(n\)\{\s*if\(RM\(\)\)return;', 'function confetti(n){if(RM()||!el.animate)return;')

# ---- inject CSS / JS ----
rep("<style>", HEAD_JS + "<style>\n" + PRE_CSS)
rep("</style>", POST_CSS + "</style>")
rep('<input type="file" id="imp" accept="application/json" class="hide">',
    '<input type="file" id="imp" accept="application/json" class="hide">' + POLY_JS)

out = src.with_name('index.safari10.html')
out.write_text(s, encoding='utf-8')
print('Wrote', out)
if miss:
    print('\nWARNING: these patterns were NOT found (file may differ from what I patched against):')
    for m in miss: print('  -', m)
else:
    print('All patches applied.')
