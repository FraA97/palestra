(() => {
  let promptEvent = null;
  const isiOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
  const standalone = () => matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
  const buttons = () => [...document.querySelectorAll('[data-install-gymsheet]')];
  const notify = message => {
    const target = document.querySelector('[data-install-message]');
    if (target) { target.textContent=message; target.hidden=false; target.scrollIntoView({behavior:'smooth',block:'nearest'}); }
    else if (typeof uiAlert === 'function') uiAlert(message,'Installa GymSheet');
    else alert(message);
  };
  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault(); promptEvent=event;
    buttons().forEach(button => button.hidden=false);
  });
  window.addEventListener('appinstalled', () => {
    promptEvent=null; buttons().forEach(button => button.textContent='✓ GymSheet installata');
  });
  document.addEventListener('click', async event => {
    const button=event.target.closest('[data-install-gymsheet]'); if(!button)return;
    if(button.id==='install-app' && /mie_schede\.html$/.test(location.pathname))return;
    if(standalone()){notify('GymSheet è già installata sul dispositivo.');return;}
    if(promptEvent){promptEvent.prompt();await promptEvent.userChoice;promptEvent=null;return;}
    notify(isiOS
      ? 'Su iPhone o iPad: apri GymSheet in Safari, tocca il pulsante Condividi e scegli “Aggiungi alla schermata Home”.'
      : 'Apri il menu del browser e scegli “Installa app” oppure “Aggiungi alla schermata Home”.');
  });
})();
