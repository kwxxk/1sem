(() => {
 document.querySelectorAll('[data-genre-mode]').forEach(button=>button.addEventListener('click',()=>{const advanced=document.body.classList.toggle('genre-advanced');button.setAttribute('aria-pressed',String(advanced));button.textContent=advanced?'기본 배열로 보기':'심화 배열로 보기';}));
 const overlap=document.querySelector('.main-page .bestseller');if(overlap){const measure=()=>document.documentElement.style.setProperty('--bestseller-overlap',Math.ceil(overlap.offsetHeight/2)+'px');measure();if('ResizeObserver'in window)new ResizeObserver(measure).observe(overlap);window.addEventListener('resize',measure);}
 if(!document.body.classList.contains('detail-page'))return;
 const params=new URLSearchParams(location.search);
 let isbn=(params.get('isbn')||'').replace(/[\s-]/g,''),title=params.get('title')||'';
 if(!isbn&&!title){isbn='9788936433598';title='채식주의자';}
 let book={title,isbn,author:params.get('author')||'',publisher:''},savedKey=null,ready=false;
 window.ThreadBook=book;
 const meta=document.getElementById('detailBookMeta'),save=document.getElementById('saveBook'),status=document.getElementById('saveStatus');
 const safeURL=value=>{try{const url=new URL(value);return['https:','http:'].includes(url.protocol)?url.href:'';}catch(_){return'';}};
 function showBook(){
  document.title=(book.title||'도서 상세')+' | ThRead';document.getElementById('book-title').textContent=book.title||'도서 상세';document.getElementById('bookAuthor').textContent=book.author||'저자 정보 확인 중';
  document.getElementById('relatedBookTitle').textContent=(book.title||'이 책')+'을 읽고 나눈 이야기';
  document.getElementById('bookDescription').textContent=book.title==='채식주의자'?'육식을 거부하기 시작한 영혜를 둘러싼 이야기를 통해 인간의 욕망과 존재의 경계를 묻는 한강의 소설입니다.':'도서 정보를 확인하고 독자들의 감상과 이야기를 나눠보세요.';
  const background=document.getElementById('detailBackground');background.src=safeURL(book.cover)||(book.title==='채식주의자'?'assets/book_detail/book_cover.jpg':'assets/nav/hero_image.jpg');
  background.onerror=()=>{background.onerror=null;background.src='assets/nav/hero_image.jpg';};
 }
 function updateSave(){save.setAttribute('aria-pressed',String(!!savedKey));document.getElementById('saveLabel').textContent=savedKey?'담기 취소':'담기';save.disabled=!ready;}
 async function loadSaved(){await ThreadAPI.ready;savedKey=null;if(ThreadAuth.getUser()){try{const data=await ThreadAPI.request('/api/bookmarks');savedKey=data.books.find(item=>book.isbn?item.isbn===book.isbn:item.title===book.title)?.key||null;}catch(e){status.textContent=e.message;}}updateSave();}
 save.addEventListener('click',()=>ThreadAuth.requireLogin(async()=>{
  save.disabled=true;try{await loadSaved();if(savedKey){await ThreadAPI.request('/api/bookmarks/'+encodeURIComponent(savedKey),{},'DELETE');savedKey=null;status.textContent='관심 도서에서 뺐습니다.';}else{const data=await ThreadAPI.request('/api/bookmarks',book);savedKey=data.key;status.textContent='내 관심 도서에 담았습니다. 마이 페이지에서 확인할 수 있습니다.';}window.dispatchEvent(new CustomEvent('thread:bookmarkschange'));}
  catch(e){status.textContent=e.message;}finally{updateSave();}
 }));
 window.addEventListener('thread:authchange',loadSaved);window.addEventListener('thread:bookmarkschange',loadSaved);
 showBook();updateSave();
 (async()=>{
  try{
   const q=new URLSearchParams({field:isbn?'isbn':'title',q:isbn||title});const data=await ThreadAPI.request('/api/books?'+q);
   const compact=value=>(value||'').replace(/\s+/g,'');const found=isbn?data.books[0]:data.books.find(item=>compact(item.title)===compact(title));
   if(!found)throw new Error('일치하는 도서 정보를 찾지 못했습니다. 도서 검색에서 정확한 ISBN 또는 판본을 선택해 주세요.');
   book=found;window.ThreadBook=book;ready=true;showBook();meta.replaceChildren();
   for(const[label,value]of[['저자',book.author],['출판사',book.publisher],['ISBN',book.isbn],['출판예정일',book.publish_date],['예정가격',book.price?book.price+'원':'정보 없음']]){const line=document.createElement('p');line.className='mb-2';line.textContent=label+' · '+(value||'정보 없음');meta.append(line);}
   const source=document.createElement('p');source.className='small opacity-75 mt-3';source.textContent='국립중앙도서관 서지정보. 예정가격은 등록 당시 기준입니다.';meta.append(source);await loadSaved();
  }catch(e){meta.textContent=e.message;}finally{window.dispatchEvent(new CustomEvent('thread:bookready'));}
 })();
 document.getElementById('writeAboutBook').addEventListener('click',()=>window.ThreadComposer?.open(window.ThreadBook));
 const libraryForm=document.getElementById('libraryForm'),libraryStatus=document.getElementById('libraryStatus'),list=document.getElementById('libraryResults'),map=document.querySelector('.library-map');
 libraryForm.addEventListener('submit',async event=>{
  event.preventDefault();const submit=libraryForm.querySelector('button');submit.disabled=true;libraryStatus.textContent='소장 도서관과 대출 상태를 조회하는 중입니다…';list.replaceChildren();
  try{
   const query=new URLSearchParams({isbn:book.isbn||'',region:document.getElementById('libraryRegion').value});const data=await ThreadAPI.request('/api/libraries?'+query);
   libraryStatus.textContent=data.message;if(!data.configured||data.approved===false)return;
   if(!data.libraries.length){libraryStatus.textContent='이 지역에서 조회되는 소장 도서관이 없습니다. '+data.message;return;}
   for(const lib of data.libraries){const li=document.createElement('li');li.className='list-group-item';const button=document.createElement('button');button.className='btn btn-link p-0 text-start';button.type='button';button.textContent=lib.name;button.addEventListener('click',()=>{map.src='https://maps.google.com/maps?q='+encodeURIComponent(lib.address||lib.name)+'&output=embed';map.title=lib.name+' 위치';});const line=document.createElement('p');line.className='small mb-1';line.textContent=lib.available===true?'대출 가능 (전일 기준)':lib.available===false?'대출 불가 (전일 기준)':'대출 상태 확인 불가';const address=document.createElement('p');address.className='small text-secondary mb-1';address.textContent=(lib.address||'')+(lib.tel?' · '+lib.tel:'');li.append(button,line,address);if(safeURL(lib.homepage)){const link=document.createElement('a');link.href=safeURL(lib.homepage);link.target='_blank';link.rel='noopener noreferrer';link.textContent='도서관 홈페이지 ↗';link.className='small';li.append(link);}list.append(li);}
   map.src='https://maps.google.com/maps?q='+encodeURIComponent(data.libraries[0].address||data.libraries[0].name)+'&output=embed';
  }catch(e){libraryStatus.textContent=e.message;}finally{submit.disabled=false;}
 });
})();
