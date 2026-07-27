(() => {
  const current=(location.pathname.split('/').pop()||'index.html').toLowerCase();
  const isActive=(names)=>names.includes(current);
  const nav=document.createElement('nav');
  nav.className='gs-header';nav.setAttribute('aria-label','Navigazione principale');
  nav.innerHTML=`
    <a class="gs-brand" href="./" aria-label="GymSheet Home"><span aria-hidden="true">🏋️</span><span>GymSheet</span></a>
    <button class="gs-menu-toggle" type="button" aria-expanded="false" aria-controls="gs-menu" aria-label="Apri menu"><span></span><span></span><span></span></button>
    <div class="gs-menu" id="gs-menu">
      <a href="landing.html" ${isActive(['landing.html','index.html'])?'aria-current="page"':''}>Home</a>
      <a href="mie_schede.html" ${isActive(['mie_schede.html'])?'aria-current="page"':''}>Le Mie Schede</a>
      <a href="editor_scheda.html" ${isActive(['editor_scheda.html'])?'aria-current="page"':''}>Editor</a>
      <details class="gs-dropdown" ${isActive(['converter.html','converter_universale.html'])?'open':''}>
        <summary ${isActive(['converter.html','converter_universale.html'])?'aria-current="page"':''}>Converter <span aria-hidden="true">▾</span></summary>
        <div><a href="converter.html">PDF / Excel</a><a href="converter_universale.html">Conversione AI</a></div>
      </details>
      <a href="istruzioni_template.html" ${isActive(['istruzioni_template.html'])?'aria-current="page"':''}>Guida</a>
      <button class="gs-install" type="button" data-install-gymsheet>Installa</button>
    </div>`;
  const style=document.createElement('style');style.textContent=`
    .gs-header{height:58px;background:#1e3a5f;color:#fff;padding:0 max(14px,env(safe-area-inset-left));display:flex;align-items:center;justify-content:space-between;gap:16px;position:sticky;top:0;z-index:4200;box-shadow:0 2px 10px rgba(15,23,42,.22);font-family:system-ui,-apple-system,Segoe UI,sans-serif}
    .gs-brand{display:flex;align-items:center;gap:8px;color:#fff;text-decoration:none;font-size:1.05rem;font-weight:850;white-space:nowrap}.gs-menu{display:flex;align-items:center;gap:3px}.gs-menu>a,.gs-dropdown>summary,.gs-install{border:0;background:transparent;color:rgba(255,255,255,.78);text-decoration:none;font:600 .79rem/1 system-ui;padding:9px 10px;border-radius:8px;cursor:pointer;list-style:none;white-space:nowrap}.gs-menu a:hover,.gs-dropdown>summary:hover,.gs-menu [aria-current="page"]{color:#fff;background:rgba(255,255,255,.16)}.gs-install{background:#16a34a;color:#fff}.gs-dropdown{position:relative}.gs-dropdown>summary::-webkit-details-marker{display:none}.gs-dropdown>div{position:absolute;right:0;top:calc(100% + 7px);min-width:190px;background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:6px;box-shadow:0 12px 30px rgba(15,23,42,.2)}.gs-dropdown>div a{display:block;color:#1f2937;text-decoration:none;padding:10px;border-radius:7px;font-size:.82rem;font-weight:650}.gs-dropdown>div a:hover{background:#eff6ff;color:#1d4ed8}.gs-menu-toggle{display:none;width:42px;height:40px;border:0;border-radius:9px;background:rgba(255,255,255,.12);padding:9px;cursor:pointer}.gs-menu-toggle span{display:block;height:2px;background:#fff;border-radius:2px;margin:4px 0;transition:.2s}
    @media(max-width:760px){.gs-header{height:56px}.gs-menu-toggle{display:block}.gs-menu{display:none;position:absolute;top:56px;left:0;right:0;background:#fff;color:#172033;padding:10px 12px 16px;box-shadow:0 12px 24px rgba(15,23,42,.22);max-height:calc(100vh - 56px);overflow:auto;align-items:stretch;gap:4px}.gs-header.menu-open .gs-menu{display:flex;flex-direction:column}.gs-menu>a,.gs-dropdown>summary,.gs-install{width:100%;color:#263449;text-align:left;font-size:.94rem;padding:13px 12px}.gs-menu a:hover,.gs-dropdown>summary:hover,.gs-menu [aria-current="page"]{color:#1d4ed8;background:#eff6ff}.gs-install{color:#fff;text-align:center;background:#16a34a;margin-top:4px}.gs-dropdown{width:100%}.gs-dropdown>div{position:static;box-shadow:none;border:0;border-left:3px solid #bfdbfe;border-radius:0;margin:0 0 4px 12px;padding:2px 0 2px 8px}.gs-dropdown>div a{padding:11px 10px}.gs-header.menu-open .gs-menu-toggle span:nth-child(1){transform:translateY(6px) rotate(45deg)}.gs-header.menu-open .gs-menu-toggle span:nth-child(2){opacity:0}.gs-header.menu-open .gs-menu-toggle span:nth-child(3){transform:translateY(-6px) rotate(-45deg)}}`;
  document.head.appendChild(style);
  document.body.prepend(nav);
  const toggle=nav.querySelector('.gs-menu-toggle');
  toggle.addEventListener('click',()=>{const open=nav.classList.toggle('menu-open');toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Chiudi menu':'Apri menu')});
  nav.addEventListener('click',e=>{if(e.target.closest('a')&&matchMedia('(max-width:760px)').matches){nav.classList.remove('menu-open');toggle.setAttribute('aria-expanded','false')}});
  document.addEventListener('click',e=>{if(!nav.contains(e.target)){nav.classList.remove('menu-open');toggle.setAttribute('aria-expanded','false')}});
})();
