/* CDH-0001 standalone design fixture. No application state, dispatch or keybindings. */
(() => {
  'use strict';
  const actors = [
    {key:'builder', name:'the builder', actor:'claude-code.*', bio:'Hardhat, stubble, cheetah overalls and jackhammer.'},
    {key:'reviewer', name:'the reviewer', actor:'kgme.review', bio:'Monocle, conspicuous teeth, spiked collar and loupe.'},
    {key:'arbiter', name:'the arbiter', actor:'arbiter.*', bio:'Skeleton judge, wizard hat, robe and star staff.'},
    {key:'guard', name:'the guard', actor:'kgme.guard', bio:'Unimpressed cherub, riot helmet, wings and X shield.'},
    {key:'scribe', name:'the scribe', actor:'kgme.*', bio:'Hooded reaper, bone hands, thick ledger and quill.'},
    {key:'michou', name:'you / Michou', actor:'michou', bio:'Bucket hat, sunglasses, chain, cheetah hoodie and flip phone.'},
    {key:'stranger', name:'the stranger', actor:'default', bio:'CRT head, crooked antennae, static face and grey coat.'}
  ];
  const modes = [
    {key:'idle', lifecycle:'ready', className:'—', event:'sample ready', tone:'live'},
    {key:'working', lifecycle:'active', className:'—', event:'sample tool intent', tone:'live'},
    {key:'waiting', lifecycle:'pending', className:'advisory', event:'sample permission request', tone:'pending'},
    {key:'transient', lifecycle:'retrying', className:'transient', event:'sample retry', tone:'transient'},
    {key:'blocked', lifecycle:'halted', className:'blocking', event:'sample halt', tone:'blocking'},
    {key:'done', lifecycle:'completed', className:'ok', event:'sample completion', tone:'ok'},
    {key:'asleep', lifecycle:'inactive', className:'—', event:'sample asleep', tone:'muted'}
  ];
  const byId = id => document.getElementById(id);
  const templates = new Map();
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const state = {actor:'builder',mode:'working',palette:'sticker',calm:false,profile:false,inView:false};
  let selected = null;
  let activeCapture = null;
  const params = new URLSearchParams(location.search);
  if (params.has('embed')) document.documentElement.classList.add('is-embed');
  const element = (tag, className, text) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = text;
    return el;
  };
  const actorFor = key => actors.find(actor => actor.key === key) || actors[6];
  const modeFor = key => modes.find(mode => mode.key === key) || modes[0];

  function artwork(actor, mode='idle', palette='phosphor', size='detail', tone) {
    const item = actorFor(actor);
    const spec = modeFor(mode);
    const svg = templates.get(item.key).cloneNode(true);
    // Standalone titles/default hide rules remain in the source SVGs. Decorative
    // inline instances use adjacent text and the shared layer, without duplicate IDs.
    svg.querySelectorAll('title,desc,style').forEach(node => node.remove());
    svg.removeAttribute('aria-labelledby');
    svg.classList.remove('is-animated');
    Object.assign(svg.dataset,{actor:item.key,mode:spec.key,palette,size,tone:tone || spec.tone});
    svg.setAttribute('aria-hidden','true');
    svg.setAttribute('focusable','false');
    svg.removeAttribute('role');
    svg.setAttribute('width',size === 'portrait' ? '24' : '72');
    svg.setAttribute('height',size === 'portrait' ? '24' : '72');
    if (size === 'portrait') svg.setAttribute('viewBox',svg.dataset.portrait || '40 24 160 160');
    return svg;
  }

  function syncMotion() {
    const enabled = !!selected && state.inView && !document.hidden && !state.calm && !reduced.matches;
    if (selected) selected.classList.toggle('is-animated',enabled);
    const reason = state.calm ? 'Calm mode: artwork hidden; all facts retained.'
      : reduced.matches ? 'System reduced motion: coherent static pose; animation removed.'
      : document.hidden ? 'Document hidden: animation removed.'
      : !state.inView ? 'Selected detail offscreen: animation removed.'
      : state.mode === 'asleep' ? 'Selected detail visible: intentional static chalk pose.'
      : 'Selected detail visible: 1 eligible animated character; all other specimens static.';
    byId('motion-status').textContent = reason;
  }

  function select(next={}) {
    if (next.actor) state.actor = actorFor(next.actor).key;
    if (next.mode) state.mode = modeFor(next.mode).key;
    if (next.palette === 'phosphor' || next.palette === 'sticker') state.palette = next.palette;
    byId('actor-select').value = state.actor;
    byId('mode-select').value = state.mode;
    byId('palette-select').value = state.palette;
    selected = artwork(state.actor,state.mode,state.palette);
    byId('selected-art').replaceChildren(selected);
    const actor = actorFor(state.actor), mode = modeFor(state.mode);
    const text = byId('selected-facts');
    text.replaceChildren(
      element('strong','',actor.name),
      element('p','facts',`Actor: ${actor.actor}. Mode: ${mode.key}.`),
      element('p','facts',`Lifecycle: ${mode.lifecycle}. Class: ${mode.className}.`),
      element('p','facts',`Event: ${mode.event}. Size: 72 CSS px. Palette: ${state.palette}.`),
      element('p','muted',actor.bio)
    );
    syncMotion();
    return diagnostics();
  }

  function setCalm(value) {
    state.calm = Boolean(value);
    document.documentElement.dataset.calm = String(state.calm);
    byId('calm-toggle').checked = state.calm;
    syncMotion();
  }

  function setProfile(value) {
    state.profile = Boolean(value);
    document.documentElement.classList.toggle('is-profile',state.profile);
    byId('profile-toggle').checked = state.profile;
  }

  function makeMatrix() {
    const table = byId('matrix');
    const head = document.createElement('thead'), tr = document.createElement('tr');
    const key = element('th','','Actor / mapping'); key.scope = 'col'; tr.append(key);
    modes.forEach(mode => {
      const th = document.createElement('th'); th.scope = 'col';
      th.append(element('div','mode-name',mode.key),element('small','',`Lifecycle: ${mode.lifecycle}`),element('small','',`Class: ${mode.className}`),element('small','',`Event: ${mode.event}`));
      tr.append(th);
    });
    head.append(tr);
    const body = document.createElement('tbody');
    actors.forEach(actor => {
      const row = document.createElement('tr'), label = document.createElement('th'); label.scope = 'row';
      label.append(element('div','actor-name',actor.name),element('div','actor-map',actor.actor),element('div','actor-bio',actor.bio));
      row.append(label);
      modes.forEach(mode => {
        const cell = document.createElement('td');
        Object.assign(cell.dataset,{actor:actor.key,mode:mode.key});
        cell.append(artwork(actor.key,mode.key)); row.append(cell);
      });
      body.append(row);
    });
    table.append(head,body);
    actors.forEach(actor => {
      const pair = element('article','pair'), art = element('div','pair-art');
      ['phosphor','sticker'].forEach(palette => { const mount = element('div'); mount.append(artwork(actor.key,'idle',palette)); art.append(mount); });
      const labels = element('div','pair-caption');labels.append(element('span','','Phosphor'),element('span','','Sticker'));
      pair.append(element('h3','',actor.name),element('p','actor-map',actor.actor),art,labels);
      byId('palette-pairs').append(pair);
    });
  }

  function makeRunList() {
    const fragment = document.createDocumentFragment();
    for (let i=0;i<50;i++) {
      const actor = actors[i % actors.length], mode = modes[i % modes.length];
      const header = element('div','run-header'); header.dataset.run = String(i+1);
      header.append(artwork(actor.key,mode.key,'phosphor','portrait'),element('span','',`Sample run ${String(i+1).padStart(2,'0')} · actor ${actor.actor}`),element('span','muted',`Mode ${mode.key} · lifecycle ${mode.lifecycle} · class ${mode.className} · event ${mode.event}`));
      const row = element('div','ledger-row');
      ['12:00:00','◀','sample:event',`Synthetic ${mode.event}`,mode.className,'0 s'].forEach((value,index) => row.append(element('span',index === 4 ? `class-${mode.className}` : '',value)));
      fragment.append(header,row);
    }
    byId('run-list').append(fragment);
  }

  function diagnostics() {
    const animations = document.getAnimations();
    const active = animations.filter(animation => animation.playState === 'running');
    return {
      ...state,hidden:document.hidden,reducedMotion:reduced.matches,
      animatedRoots:document.querySelectorAll('.chibi.is-animated').length,
      activeAnimations:active.length,animationNames:active.map(animation => animation.animationName || 'unknown'),
      matrixCells:document.querySelectorAll('#matrix tbody td').length,
      staticRunPortraits:document.querySelectorAll('#run-list .chibi[data-size="portrait"]').length,
      activePortraitAnimations:active.filter(animation => animation.effect?.target?.closest('.chibi[data-size="portrait"]')).length,
      devicePixelRatio:window.devicePixelRatio,viewport:{width:innerWidth,height:innerHeight},userAgent:navigator.userAgent
    };
  }

  const summarize = values => {
    if (!values.length) return {count:0};
    const sorted = [...values].sort((a,b) => a-b), percentile = p => sorted[Math.min(sorted.length-1,Math.floor((sorted.length-1)*p))];
    return {count:values.length,mean:values.reduce((a,b) => a+b,0)/values.length,p50:percentile(.5),p95:percentile(.95),p99:percentile(.99),max:sorted[sorted.length-1],over50ms:values.filter(value => value>50).length};
  };

  async function profile({duration=30000,calm=false}={}) {
    if (activeCapture) throw new Error('A profile capture is already running.');
    if (document.hidden) throw new Error('Bring the fixture into view before profiling.');
    if (!Number.isFinite(duration) || duration < 1000 || duration > 60000) throw new Error('Capture duration must be between 1000 and 60000 ms.');
    setProfile(true);setCalm(calm);
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    const start = performance.now(), initial = diagnostics(), intervals=[], longTasks=[], inputLatencies=[],scrollLatencies=[];
    let previous, frame, timer, observer;
    const buttons = [byId('profile-motion'),byId('profile-calm')];
    buttons.forEach(button => {button.disabled=true;});
    byId('profile-report').textContent = `Capturing ${duration/1000} seconds with calm ${Boolean(calm)}. Scroll the 50-run list and type in the fixture input probe to collect interaction samples.`;
    return new Promise(resolve => {
      const capture = {finish:null}; activeCapture=capture;
      const onInput = () => { const eventAt=performance.now();requestAnimationFrame(() => {if(activeCapture===capture) inputLatencies.push(performance.now()-eventAt);}); };
      const onScroll = () => { const eventAt=performance.now();requestAnimationFrame(() => {if(activeCapture===capture) scrollLatencies.push(performance.now()-eventAt);}); };
      const onHidden = () => {if(document.hidden) finish('document hidden');};
      const finish = reason => {
        if(activeCapture !== capture) return;
        cancelAnimationFrame(frame);clearTimeout(timer);observer?.disconnect();
        document.removeEventListener('visibilitychange',onHidden);
        byId('input-probe').removeEventListener('input',onInput);byId('run-list').removeEventListener('scroll',onScroll);
        const result = {
          capture:'CDH-0001 standalone fixture',timestamp:new Date().toISOString(),requestedMs:duration,elapsedMs:performance.now()-start,reason,
          initial,final:diagnostics(),frameIntervalMs:summarize(intervals),
          longTasksSupported:PerformanceObserver.supportedEntryTypes?.includes('longtask') || false,
          longTasks:{count:longTasks.length,totalMs:longTasks.reduce((a,b)=>a+b,0),maxMs:longTasks.length?Math.max(...longTasks):0},
          inputEventToNextFrameMs:summarize(inputLatencies),scrollEventToNextFrameMs:summarize(scrollLatencies),
          limits:'Frame intervals are observed RAF cadence, not GPU render time. Input/scroll latency begins at event handling, not hardware input. No interaction samples means unverified. This fixture does not certify future cockpit performance.'
        };
        activeCapture=null;buttons.forEach(button=>{button.disabled=false;});
        byId('profile-report').textContent=JSON.stringify(result,null,2);resolve(result);
      };
      capture.finish=finish;
      if(PerformanceObserver.supportedEntryTypes?.includes('longtask')) {
        observer=new PerformanceObserver(list=>list.getEntries().forEach(entry=>longTasks.push(entry.duration)));
        observer.observe({type:'longtask',buffered:false});
      }
      const tick = now => {if(previous !== undefined) intervals.push(now-previous);previous=now;frame=requestAnimationFrame(tick);};
      frame=requestAnimationFrame(tick);timer=setTimeout(()=>finish('completed'),duration);
      byId('input-probe').addEventListener('input',onInput);byId('run-list').addEventListener('scroll',onScroll,{passive:true});
      document.addEventListener('visibilitychange',onHidden);
    });
  }

  const ready = (async () => {
    await Promise.all(actors.map(async actor => {
      const response=await fetch(new URL(`./${actor.key}.svg`,document.baseURI),{cache:'no-cache'});
      if(!response.ok) throw new Error(`${actor.key}.svg returned ${response.status}`);
      const parsed=new DOMParser().parseFromString(await response.text(),'image/svg+xml');
      if(parsed.querySelector('parsererror') || parsed.documentElement.localName!=='svg') throw new Error(`${actor.key}.svg is not valid SVG`);
      templates.set(actor.key,document.importNode(parsed.documentElement,true));
    }));
    actors.forEach(actor => {const option=element('option','',actor.name);option.value=actor.key;byId('actor-select').append(option);});
    modes.forEach(mode=>{const option=element('option','',mode.key);option.value=mode.key;byId('mode-select').append(option);});
    makeMatrix();makeRunList();
    document.querySelectorAll('[data-art]').forEach(mount=>mount.append(artwork(mount.dataset.art,mount.dataset.mode,mount.dataset.palette,mount.dataset.size)));
    select();setProfile(params.has('profile'));
    byId('actor-select').addEventListener('change',event=>select({actor:event.target.value}));
    byId('mode-select').addEventListener('change',event=>select({mode:event.target.value}));
    byId('palette-select').addEventListener('change',event=>select({palette:event.target.value}));
    byId('calm-toggle').addEventListener('change',event=>setCalm(event.target.checked));
    byId('profile-toggle').addEventListener('change',event=>setProfile(event.target.checked));
    byId('profile-motion').addEventListener('click',()=>profile({calm:false}).catch(error=>{byId('profile-report').textContent=error.message;}));
    byId('profile-calm').addEventListener('click',()=>profile({calm:true}).catch(error=>{byId('profile-report').textContent=error.message;}));
    reduced.addEventListener('change',syncMotion);document.addEventListener('visibilitychange',syncMotion);
    new IntersectionObserver(entries=>{state.inView=entries[0].isIntersecting && entries[0].intersectionRatio>=.5;syncMotion();},{threshold:[0,.5,1]}).observe(byId('selected-art'));
    return diagnostics();
  })();
  ready.catch(error=>{byId('fixture-error').textContent=`Artwork could not load: ${error.message}. Open this folder through a local HTTP server with all 7 SVG files beside preview.html. Native .dc.html support is supplied by Cowork's canvas, not this fixture.`;});
  window.chibiFixture=Object.freeze({ready,select,setCalm,setProfile,diagnostics,profile,actors,modes});
})();
