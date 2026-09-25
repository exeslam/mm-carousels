// ds-mm-apple · Liquid Glass: преломление по краям для каждой стеклянной карточки.
// Для каждого .t / .pill строится карта смещения (canvas) под его точный размер и радиус:
// у края фон «затягивается» линзой, в центре остаётся почти прозрачным.
// Работает в Chromium (backdrop-filter: url(#svg-filter)), которым рендерятся PNG.
(function(){
  const NS='http://www.w3.org/2000/svg';
  const svg=document.createElementNS(NS,'svg');svg.setAttribute('width','0');svg.setAttribute('height','0');
  svg.style.position='absolute';document.body.prepend(svg);
  function sdf(px,py,hw,hh,r){ // расстояние до края скруглённого прямоугольника (внутри > 0)
    const qx=Math.abs(px)-(hw-r),qy=Math.abs(py)-(hh-r);
    const out=Math.hypot(Math.max(qx,0),Math.max(qy,0))+Math.min(Math.max(qx,qy),0)-r;return -out;}
  function map(w,h,r,bezel){
    const c=document.createElement('canvas');c.width=w;c.height=h;const ctx=c.getContext('2d');const img=ctx.createImageData(w,h);
    const hw=w/2,hh=h/2;
    for(let y=0;y<h;y++)for(let x=0;x<w;x++){
      const px=x+.5-hw,py=y+.5-hh,d=sdf(px,py,hw,hh,r);let dx=0,dy=0;
      if(d>0&&d<bezel){
        const gx=sdf(px+1,py,hw,hh,r)-sdf(px-1,py,hw,hh,r),gy=sdf(px,py+1,hw,hh,r)-sdf(px,py-1,hw,hh,r);
        const len=Math.hypot(gx,gy)||1;const t=1-d/bezel;const m=Math.pow(t,2.2); // выпуклый профиль линзы
        dx=-gx/len*m;dy=-gy/len*m;} // сэмплируем снаружи: край «собирает» фон, как толстое стекло
      const i=(y*w+x)*4;img.data[i]=128+dx*127;img.data[i+1]=128+dy*127;img.data[i+2]=128;img.data[i+3]=255;}
    ctx.putImageData(img,0,0);return c.toDataURL();}
  let n=0;
  document.querySelectorAll('.lgk').forEach(el=>{
    const b=el.getBoundingClientRect();const w=Math.round(b.width),h=Math.round(b.height);if(w<10||h<10)return;
    const r=Math.min(parseFloat(getComputedStyle(el).borderTopLeftRadius)||0,h/2,w/2);
    const isPill=el.classList.contains('pill')||el.classList.contains('kw')||el.classList.contains('note');const bezel=isPill?18:46,scale=isPill?40:90,blur=isPill?1.2:el.matches(".blue,.navy")?5:3.5;
    const id='lg'+(n++);const f=document.createElementNS(NS,'filter');
    f.setAttribute('id',id);f.setAttribute('x','0');f.setAttribute('y','0');f.setAttribute('width','1');f.setAttribute('height','1');
    f.setAttribute('color-interpolation-filters','sRGB');
    f.innerHTML=`<feImage href="${map(w,h,r,bezel)}" x="0" y="0" width="${w}" height="${h}" preserveAspectRatio="none" result="m"/>`+
      `<feGaussianBlur in="SourceGraphic" stdDeviation="${blur}" result="b"/>`+
      `<feDisplacementMap in="b" in2="m" scale="${scale}" xChannelSelector="R" yChannelSelector="G" result="d"/>`+
      `<feColorMatrix in="d" type="saturate" values="1.7"/>`;
    f.setAttribute('filterUnits','userSpaceOnUse');f.setAttribute('primitiveUnits','userSpaceOnUse');
    f.setAttribute('width',w);f.setAttribute('height',h);
    svg.appendChild(f);el.style.backdropFilter=`url(#${id})`;el.style.webkitBackdropFilter=`url(#${id})`;
  });
  document.documentElement.dataset.liquid=String(n);
})();
