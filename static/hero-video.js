'use strict';
(()=>{const video=document.getElementById('heroVideo');if(!video)return;const reduced=matchMedia('(prefers-reduced-motion: reduce)');let visible=false,loaded=false,failed=false;video.muted=true;video.defaultMuted=true;
function sync(){if(!visible||document.hidden||reduced.matches||failed){video.pause();return;}if(!loaded){loaded=true;video.src=video.dataset.src;video.load();}video.play().catch(()=>{});}
video.addEventListener('playing',()=>video.classList.add('is-playing'));video.addEventListener('error',()=>{failed=true;video.classList.remove('is-playing');});document.addEventListener('visibilitychange',sync);reduced.addEventListener('change',sync);new IntersectionObserver(e=>{visible=e[0].isIntersecting;sync();},{threshold:.1}).observe(video.closest('.hero'));
})();
