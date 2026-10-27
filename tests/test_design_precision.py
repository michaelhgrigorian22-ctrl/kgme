"""CDH-0031: precision rules plus real CSS-projection column baselines.

The static checks cover stylesheet, inline and generated style declarations.
The baseline check evaluates the committed board components, mounts the tray,
and measures their CSS in the installed Chromium at canvas.json design sizes.
It requires the existing Node and Chrome tools, never installs a dependency,
serves no HTTP page, and blocks external resources. It is part of make check.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from test_design_contrast import Markup, clean, declarations, rules

DESIGN = Path(__file__).resolve().parents[1] / "docs/design/cockpit-v0"
FILES = tuple(sorted(path.name for path in DESIGN.glob("*.dc.html"))) + ("station/index.html",)
SIZES = {9, 11, 12, 14, 22}
EASING = "cubic-bezier(0,0,.2,1)"
DURATIONS = {"120ms", "240ms", "480ms", ".12s", ".24s", ".48s", "0.12s", "0.24s", "0.48s"}
SPACING = re.compile(r"(?:padding|margin)(?:-[\w-]+)?|(?:row-|column-)?gap")
ROW_CLASSES = {
    "row",
    "ledger-row",
    "grp",
    "chip",
    "kbd",
    "key",
    "quota-alert",
    "selection-band",
    "tr-row",
    "tr-bar",
    "tr-open",
    "tr-col",
    "tr-head",
    "tr-l1",
    "tr-l2",
    "tr-context-copy",
    "tr-context-strip",
    "tr-chip",
    "tr-kbd",
    "tr-life",
    "tr-lbl",
    "tr-foot",
    "tr-rules",
    "tr-empty",
    "chip-room",
    "col",
    "ctl",
    "head",
    "lines",
}
RULE_GAPS = {"activity-chart"}
SEMANTIC_BORDER = {"#39d0ff", "#ff3d7f", "#ffb02e", "#4de38a", "#3a4650", "#a3b0b8"}
BASELINE_COUNTS = {
    name: 3 for name in ("Main", "Empty", "Blocking", "Pending", "Disconnected", "Phase2")
}
BASELINE_COUNTS["Wall"] = 4


def records(source):
    """Yield declaration context without treating commented examples as rules."""
    yield from rules(source)
    for node in Markup(source).nodes:
        if node.attrs.get("style"):
            context = " ".join(
                ancestor.tag + "." + ".".join((ancestor.attrs.get("class") or "").split())
                for ancestor in node.ancestors()
            )
            yield context, declarations(node.attrs["style"])
    # Template-generated style values are literal CSS strings in renderVals.
    for script in re.findall(
        r"<script[^>]*data-dc-script[^>]*>(.*?)</script>", clean(source), re.S
    ):
        for match in re.finditer(
            r"(?<![-\w])(padding(?:-[\w-]+)?|margin(?:-[\w-]+)?|(?:row-|column-)?gap|"
            r"font-size|line-height|letter-spacing|transition(?:-[\w-]+)?|animation(?:-[\w-]+)?|"
            r"border(?:-[\w-]+)?)\s*:\s*([^;}'\"\n]+)",
            script,
        ):
            yield "generated style", {match.group(1): match.group(2).strip()}


def context_classes(context):
    return set(re.findall(r"\.([\w-]+)", context))


@pytest.mark.parametrize("file", FILES)
def test_spacing_stays_on_the_grid(file):
    failures = []
    for context, props in records((DESIGN / file).read_text()):
        classes = context_classes(context)
        for prop, value in props.items():
            if not SPACING.fullmatch(prop):
                continue
            for match in re.finditer(r"(-?\d*\.?\d+)px", value):
                number = float(match.group(1))
                permitted = number % 8 == 0
                permitted |= number % 4 == 0 and bool(classes & ROW_CLASSES)
                permitted |= (
                    number == 3
                    and prop.startswith("padding")
                    and bool(classes & {"row", "ledger-row", "tr-row"})
                )
                permitted |= number == 1 and "gap" in prop and bool(classes & RULE_GAPS)
                permitted |= (
                    number == -1 and prop == "margin" and bool(classes & {"vh", "sr-only", "tr-vh"})
                )
                if not permitted:
                    failures.append((context, prop, value, number))
    assert not failures, (file, failures)


@pytest.mark.parametrize("file", FILES)
def test_type_scale_tracking_and_tabular_numbers(file):
    source = (DESIGN / file).read_text()
    body = {}
    for selector, props in rules(source):
        if "body" in selector.split(","):
            body.update(props)
    assert body.get("font-variant-numeric") == "tabular-nums", (
        file,
        "Numeric inheritance must be tabular",
    )
    failures = []
    for context, props in records(source):
        for prop, value in props.items():
            value = value.replace("!important", "").strip()
            if prop == "font-size" and (not value.endswith("px") or float(value[:-2]) not in SIZES):
                failures.append((context, prop, value))
            if prop == "letter-spacing" and value not in {
                "0",
                "0em",
                ".14em",
                "0.14em",
                ".1em",
                "0.1em",
            }:
                failures.append((context, prop, value))
            if prop == "font-variant-numeric" and value != "tabular-nums":
                failures.append((context, prop, value))
            if prop == "font-stretch" and value != "normal":
                failures.append((context, prop, value))
            if prop == "line-height" and value not in {
                "1",
                "1.45",
                "13px",
                "14px",
                "15px",
                "16px",
                "18px",
            }:
                failures.append((context, prop, value))
    assert not failures, (file, failures)


@pytest.mark.parametrize("file", FILES)
def test_structural_borders_share_one_muted_value(file):
    failures = []
    for context, props in records((DESIGN / file).read_text()):
        classes = context_classes(context)
        for prop, value in props.items():
            if not prop.startswith("border") or "radius" in prop:
                continue
            colours = set(re.findall(r"#[\da-fA-F]{6}\b", value))
            exceptions = set()
            if {"phase2", "kbd"} <= classes or {"buf", "full"} <= classes:
                exceptions.add("#6f8290")  # Dashed/inactive controls remain visually reserved.
            if "future-path" in classes:
                exceptions.add("#7a8d9b")  # The future interaction's causal guide is semantic.
            if colours - {"#1e2a33"} - SEMANTIC_BORDER - exceptions:
                failures.append((context, prop, value, "unclassified border colour"))
            widths = {float(width) for width in re.findall(r"(?<![\w.-])(\d*\.?\d+)px", value)}
            if widths - {0, 1}:
                if widths == {3} and classes & {"frame", "mini"} and "#ffb02e" in value:
                    continue  # The pending frame stripe is not a structural divider.
                if widths == {2} and "future-path" in classes and "#7a8d9b" in value:
                    continue
                if widths != {2} or not ("#39d0ff" in value or "var(--cyan)" in value):
                    failures.append((context, prop, value, "structural border is not one pixel"))
    assert not failures, (file, failures)


def motion_parts(value):
    """Split transition lists without splitting cubic-bezier arguments."""
    return re.split(r",(?![^()]*\))", value)


@pytest.mark.parametrize("file", FILES)
def test_motion_uses_one_curve_three_durations_and_one_reduced_query(file):
    source = clean((DESIGN / file).read_text())
    assert len(re.findall(r"@media\s*\(prefers-reduced-motion\s*:\s*reduce\)", source)) == 1, file
    variables = {}
    for _, props in records(source):
        for prop, value in props.items():
            if prop.startswith("--"):
                variables.setdefault(prop, set()).add(value)
    prefix = "--" if file == "station/index.html" else "--precision-"
    for name, expected in {
        "response": "120ms",
        "state": "240ms",
        "travel": "480ms",
        "ease": EASING,
    }.items():
        assert variables.get(prefix + name) == {expected}, (
            file,
            name,
            variables.get(prefix + name),
        )

    def resolve_timing(value):
        def replacement(match):
            values = variables.get(match.group(1), set())
            assert len(values) == 1, (file, match.group(1), "Ambiguous timing variable", values)
            return next(iter(values))

        return re.sub(r"var\((--[\w-]+)\)", replacement, value)

    failures = []
    for context, props in records(source):
        for prop, original in props.items():
            if not (
                prop.startswith("transition")
                or prop.startswith("animation")
                or prop.endswith("-motion")
            ):
                continue
            value = original.replace("!important", "").strip()
            if value in {"none", "0s", "0ms"}:
                continue
            if prop.startswith("animation") and value.startswith("var(--"):
                assert re.fullmatch(r"var\(--[\w-]+-motion,none\)", value), (file, context, value)
                continue  # Each custom motion definition is checked below.
            value = resolve_timing(value)
            if re.search(r"(?:^|\s)(?:blink|chibi-[\w-]+)(?:\s|$)", value):
                continue  # Documented cursor and selected crew ambient motions.
            if prop in {"transition-delay", "animation-delay"}:
                failures.append((context, prop, original, "feedback must begin within one frame"))
                continue
            if prop == "transition-property" or prop in {
                "animation-fill-mode",
                "animation-play-state",
            }:
                continue
            if prop.endswith("timing-function"):
                if value.replace(" ", "") != EASING:
                    failures.append((context, prop, original))
                continue
            if prop.endswith("duration"):
                if any(part.strip() not in DURATIONS for part in value.split(",")):
                    failures.append((context, prop, original))
                continue
            for part in motion_parts(value):
                times = re.findall(r"(?<![\w.-])(?:\d*\.)?\d+(?:ms|s)\b", part)
                if (
                    len(times) != 1
                    or times[0] not in DURATIONS
                    or EASING not in part.replace(" ", "")
                ):
                    failures.append((context, prop, original))
    assert not failures, (file, failures)


def test_station_programmatic_motion_uses_the_same_rulebook():
    source = (DESIGN / "station/index.html").read_text()
    motion = re.search(r"const MOTION\s*=\s*\{([^}]+)\}", source)
    assert motion, "The station's programmatic animation timings must remain explicit"
    values = dict(re.findall(r"(response|state|travel)\s*:\s*(\d+)", motion.group(1)))
    assert values == {"response": "120", "state": "240", "travel": "480"}
    easing = re.search(r"easing\s*:\s*['\"]([^'\"]+)['\"]", motion.group(1))
    assert easing and easing.group(1).replace(" ", "") == EASING


# No local server or npm package is involved. The source-only projection is the
# same template expansion used for CDH-0027/0032 acceptance, now kept in the gate.
PROJECTION = r"""
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const {spawn} = require('node:child_process');
const [design, chromePath, profile] = process.argv.slice(1);
const read = p => fs.readFileSync(path.join(design,p),'utf8');
function component(s,props={}) {
  const C=vm.runInNewContext(s.match(/<script[^>]*data-dc-script[^>]*>([\s\S]*?)<\/script>/)[1]+'\nComponent',
    {DCLogic:class {props={};setState(s){Object.assign(this.state,s);}}});
  const o=new C();o.props=props;return o;
}
const escape=v=>String(v??'').replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');
function value(e,c){e=e.replace(/^{{|}}$/g,'').trim();return e==='true'?true:e==='false'?false:e.split('.').reduce((v,k)=>v?.[k],c);}
function project(html,ctx){
  let m;
  while((m=/<sc-(for|if)\b([^>]*)>/.exec(html))){
    let depth=1,end,close,t;const tags=/<\/?sc-(?:for|if)\b[^>]*>/g;
    tags.lastIndex=m.index+m[0].length;
    while((t=tags.exec(html))){depth+=t[0].startsWith('</')?-1:1;if(!depth){end=t.index;close=tags.lastIndex;break;}}
    if(end===undefined)throw Error('Unclosed projection template');
    const body=html.slice(m.index+m[0].length,end),expr=m[2].match(/(?:list|value)="([^"]*)"/)[1],val=value(expr,ctx);
    let result='';
    if(m[1]==='for'){const alias=m[2].match(/as="([^"]*)"/)[1];result=(val||[]).map(v=>project(body,{...ctx,[alias]:v})).join('');}
    else if(val)result=project(body,ctx);
    html=html.slice(0,m.index)+result+html.slice(close);
  }
  return html.replace(/ onClick="{{[^}]+}}"/g,'').replace(/{{\s*([^}]+?)\s*}}/g,(_,e)=>escape(value(e,ctx)));
}
const css=s=>[...s.matchAll(/<style>([\s\S]*?)<\/style>/g)].map(m=>m[1]).join('\n');
const html=s=>s.match(/<x-dc>([\s\S]*?)<\/x-dc>/)[1].replace(/<helmet>[\s\S]*?<\/helmet>/,'');
const canvas=JSON.parse(read('canvas.json')),tray=read('Tray.dc.html');
const chrome=spawn(chromePath,['--headless','--no-sandbox','--remote-debugging-pipe','--no-first-run',
  '--no-default-browser-check','--disable-background-networking','--disable-component-update',
  '--disable-sync','--disable-extensions','--proxy-server=http://127.0.0.1:9','--user-data-dir='+profile],
  {stdio:['ignore','ignore','pipe','pipe','pipe']});
let seq=0,buf='',stderr='';const pending=new Map();
chrome.stderr.on('data',chunk=>{stderr=(stderr+chunk).slice(-8000);});
function send(method,params={},sessionId){return new Promise((resolve,reject)=>{
  const id=++seq,timer=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout '+method));},20000);
  pending.set(id,{resolve,reject,timer});chrome.stdio[3].write(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})})+'\0');
});}
chrome.stdio[4].on('data',chunk=>{buf+=chunk.toString();let n;while((n=buf.indexOf('\0'))>=0){
  const s=buf.slice(0,n);buf=buf.slice(n+1);if(!s)continue;const m=JSON.parse(s),p=pending.get(m.id);
  if(!p)continue;pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);
}});
chrome.on('exit',code=>{for(const p of pending.values()){clearTimeout(p.timer);p.reject(Error('Chrome exited '+code+' '+stderr));}pending.clear();});
async function evaluate(s,expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true},s);if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
(async()=>{const result={};try{
  await send('Browser.getVersion');
  for(const [file,size]of Object.entries(canvas.boards)){
    const source=read(file),vals=component(source,{calm:false}).renderVals();
    let mark=html(source).replace(/<dc-import\b([^>]*)><\/dc-import>/g,(_,attrs)=>{
      const props={calm:false};for(const [,key,v]of attrs.matchAll(/(\w+)="([^"]+)"/g)){
        if(key==='name'||key==='hint-size')continue;props[key]=v.startsWith('{{')?value(v,vals):v;
      }return project(html(tray),component(tray,props).renderVals());
    });
    mark=project(mark,vals);if(mark.includes('{{')||mark.includes('<dc-import'))throw Error(file+' incomplete projection');
    const {targetId}=await send('Target.createTarget',{url:'about:blank'}),{sessionId:s}=await send('Target.attachToTarget',{targetId,flatten:true});
    await send('Page.enable',{},s);await send('Network.enable',{},s);await send('Network.setBlockedURLs',{urls:['*']},s);
    await send('Emulation.setDeviceMetricsOverride',{width:size.w,height:size.h,deviceScaleFactor:1,mobile:false},s);
    await send('Page.bringToFront',{},s);
    const {frameTree}=await send('Page.getFrameTree',{},s);
    await send('Page.setDocumentContent',{frameId:frameTree.frame.id,html:'<!doctype html><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'"><style>'+css(tray)+css(source)+'</style>'+mark},s);
    await evaluate(s,'new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');
    result[file]=await evaluate(s,`({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,groups:[...document.querySelectorAll('[data-precision-columns]')].map((g,index)=>({index,columns:[...g.children].filter(c=>c.hasAttribute('data-precision-column')).map(c=>{const r=c.getBoundingClientRect(),style=getComputedStyle(c),grid=getComputedStyle(g).gridTemplateColumns,tracks=grid==='none'?0:grid.trim().split(' ').filter(Boolean).length,span=style.gridColumnStart.split(' ');return {top:r.top,bottom:r.bottom,left:r.left,right:r.right,width:r.width,height:r.height,scrollWidth:c.scrollWidth,clientWidth:c.clientWidth,scrollHeight:c.scrollHeight,clientHeight:c.clientHeight,overflowX:style.overflowX,overflowY:style.overflowY,gridColumnStart:style.gridColumnStart,gridColumnEnd:style.gridColumnEnd,tracks,fullSpan:(style.gridColumnStart==='1'&&style.gridColumnEnd==='-1')||!!(tracks&&span[0]==='span'&&Number(span[1])===tracks)}})}))})`);
    result[file].rows=await evaluate(s,`[...document.querySelectorAll('.row')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility==='visible';}).map(e=>{const r=e.getBoundingClientRect(),c=getComputedStyle(e);return {text:e.textContent.trim().slice(0,120),top:r.top,bottom:r.bottom,height:r.height,paddingTop:parseFloat(c.paddingTop),paddingBottom:parseFloat(c.paddingBottom),contentTop:r.top+parseFloat(c.paddingTop)+parseFloat(c.borderTopWidth),contentBottom:r.bottom-parseFloat(c.paddingBottom)-parseFloat(c.borderBottomWidth),cells:[...e.children].map(cell=>{const b=cell.getBoundingClientRect();return {text:cell.textContent.trim().slice(0,80),top:b.top,bottom:b.bottom,height:b.height};})}})`);
    await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9},s);
    await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9},s);
    result[file].focus=await evaluate(s,`(()=>{
      const style=document.createElement('style');
      style.textContent='*,*::before,*::after{transition:none!important;animation:none!important}';
      document.head.append(style);
      const visible=e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility==='visible'&&!e.closest('[hidden]');};
      const read=e=>{const c=getComputedStyle(e);return {label:(e.getAttribute('aria-label')||e.textContent).trim().slice(0,100),tag:e.tagName,classes:e.className,outlineWidth:c.outlineWidth,outlineStyle:c.outlineStyle,outlineColor:c.outlineColor,outlineOffset:c.outlineOffset};};
      const states=[...document.querySelectorAll('.focus,.tr-focus')].filter(visible).map(read);
      const controls=[];
      for(const e of document.querySelectorAll('button,a[href],[tabindex],summary')){
        if(!visible(e)||e.disabled||e.getAttribute('tabindex')==='-1'||e.closest('[aria-disabled="true"]'))continue;
        e.focus({preventScroll:true});controls.push({...read(e),focused:document.activeElement===e});
      }
      return {controls,states};
    })()`);
    await send('Target.closeTarget',{targetId});
  }
  process.stdout.write(JSON.stringify(result));
}finally{try{await send('Browser.close');}catch{}chrome.kill();}})().catch(e=>{console.error(e.stack);process.exitCode=1;chrome.kill();});
"""  # noqa: E501 (embedded source-only Node/CDP fixture)


@pytest.fixture(scope="module")
def projected_columns(tmp_path_factory):
    node = shutil.which("node")
    chrome = next(
        (
            str(candidate)
            for candidate in (
                Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                Path(shutil.which("google-chrome") or "/nonexistent"),
                Path(shutil.which("chromium") or "/nonexistent"),
            )
            if candidate.is_file()
        ),
        None,
    )
    assert node and chrome, "Precision baseline gate requires the existing Node and Chrome tools"
    profile = tmp_path_factory.mktemp("precision-chrome")
    run = subprocess.run(
        [node, "-e", PROJECTION, str(DESIGN), chrome, str(profile)],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


@pytest.mark.parametrize("file", FILES[:-1])
def test_projected_columns_share_top_and_bottom_baselines(file, projected_columns):
    projection = projected_columns[file]
    groups = projection["groups"]
    assert projection["scrollWidth"] <= projection["width"] + 1, (
        file,
        "Projection exceeds its design width",
        projection,
    )
    name = file.removesuffix(".dc.html")
    if name in BASELINE_COUNTS:
        assert any(len(group["columns"]) == BASELINE_COUNTS[name] for group in groups), (
            file,
            "Missing primary column baseline contract",
            groups,
        )
    elif name in {"Components", "Sprites", "Tray"}:
        assert groups, (file, "Reference-board column groups must be measured")
    for group in groups:
        columns = group["columns"]
        assert len(columns) >= 2, (file, group)
        assert all(column["height"] > 0 and column["width"] > 0 for column in columns), (
            file,
            group,
        )
        for column in columns:
            assert column["left"] >= -1 and column["right"] <= projection["width"] + 1, (
                file,
                column,
            )
            for axis in ("Width", "Height"):
                overflow = column["overflowX" if axis == "Width" else "overflowY"]
                assert (
                    overflow in {"auto", "scroll"}
                    or column["scroll" + axis] <= column["client" + axis] + 1
                ), (file, "Column contents overrun their measured box", column)
        rows = []
        for column in sorted(columns, key=lambda col: col["top"]):
            if rows and column["top"] < max(item["bottom"] for item in rows[-1]) - 1:
                rows[-1].append(column)
            else:
                rows.append([column])
        for row in rows:
            assert len(row) >= 2 or row[0]["fullSpan"], (
                file,
                "A marked column group has no shared horizontal baseline",
                [(c["gridColumnStart"], c["gridColumnEnd"], c["tracks"]) for c in row],
            )
            assert (
                max(column["top"] for column in row) - min(column["top"] for column in row) <= 1
            ), (file, "Columns start on different baselines", row)
            assert (
                max(column["bottom"] for column in row) - min(column["bottom"] for column in row)
                <= 1
            ), (file, "Columns end on different baselines", row)
        if name in BASELINE_COUNTS and len(columns) == BASELINE_COUNTS[name]:
            assert len(rows) == 1, (file, "Primary columns do not start on one baseline", columns)


@pytest.mark.parametrize("file", FILES[:-1])
def test_computed_focus_ring_is_common_on_controls_and_selected_rows(file, projected_columns):
    focus = projected_columns[file]["focus"]
    assert focus["controls"], (file, "No enabled focusable control was measured")
    for control in focus["controls"]:
        assert control["focused"], (file, "Control refused focus", control)
    for item in focus["controls"] + focus["states"]:
        assert (
            item["outlineWidth"],
            item["outlineStyle"],
            item["outlineColor"],
            item["outlineOffset"],
        ) == ("2px", "solid", "rgb(57, 208, 255)", "-2px"), (file, item)


@pytest.mark.parametrize("file", FILES[:-1])
def test_computed_ledger_cells_stay_inside_their_twenty_two_pixel_row(file, projected_columns):
    rows = projected_columns[file]["rows"]
    if file in {
        "Main.dc.html",
        "Blocking.dc.html",
        "Pending.dc.html",
        "Disconnected.dc.html",
        "Phase2.dc.html",
        "Wall.dc.html",
        "Components.dc.html",
    }:
        assert rows, (file, "Ledger row geometry was not measured")
    for row in rows:
        assert abs(row["height"] - 22) <= 0.1, (file, "Ledger row height changed", row)
        assert row["paddingTop"] == row["paddingBottom"] == 3, (
            file,
            "The documented three-pixel row inset changed",
            row,
        )
        assert row["cells"], (file, "Ledger row has no measured cells", row)
        for cell in row["cells"]:
            # One pixel permits fractional font metrics; a wrapped second line
            # exceeds this by a whole line and must fail before touching a rule.
            assert (
                cell["top"] >= row["contentTop"] - 1 and cell["bottom"] <= row["contentBottom"] + 1
            ), (file, "A ledger cell crosses its content inset or divider", row, cell)
