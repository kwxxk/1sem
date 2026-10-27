// 키를 포함하지 않는 로컬 서버만 호출합니다.
(() => {
 const form = document.getElementById('bookSearchForm');
 if (!form) return;
 const input = document.getElementById('bookQuery');
 const field = document.getElementById('bookField');
 const results = document.getElementById('bookResults');
 const status = document.getElementById('searchStatus');
 const previous = document.getElementById('previousBooks');
 const next = document.getElementById('nextBooks');
 const pageLabel = document.getElementById('booksPage');
 const pagination=document.getElementById('bookPagination');

 const submit = form.querySelector('[type="submit"]');
 let currentPage = 1, currentQuery = '', currentField = 'title', controller;

 const fallback = 'assets/book-placeholder.svg';

 function text(tag, value, className) {
  const element = document.createElement(tag);
  element.textContent = value;
  if (className) element.className = className;
  return element;
 }
 function date(value) {
  return /^\d{8}$/.test(value) ? value.slice(0,4)+'.'+value.slice(4,6)+'.'+value.slice(6,8) : value || '정보 없음';
 }
 function showDetail(book) { location.href=ThreadBooks.url(book); }
 function render(books) {
  results.replaceChildren();
  for (const book of books) {
   const column = text('div','','col-12 col-sm-6 col-lg-4');
   const card = text('article','','card api-book-card h-100');
   const body = text('div','','card-body d-flex flex-column');
   const image = document.createElement('img');
   image.className = 'api-book-cover'; image.alt = (book.title || '도서') + ' 표지'; image.loading = 'lazy';
   let cover;
   try { cover = new URL(book.cover); } catch (_) { cover = null; }
   image.src = cover && ['http:','https:'].includes(cover.protocol) ? cover.href : fallback;
   image.addEventListener('error',()=>{ if (!image.src.endsWith('book-placeholder.svg')) image.src = fallback; });
   body.append(text('h3',book.title || '제목 정보 없음','card-title fs-6'),text('p',book.author || '저자 정보 없음','mb-2 text-secondary small'),text('p',book.publisher || '출판사 정보 없음','mb-2 small'),text('p','ISBN '+(book.isbn || '정보 없음'),'small mb-2'),text('p','출판예정일 '+date(book.publish_date),'small text-secondary'));
   const button = text('button','상세 정보','btn btn-outline-secondary btn-sm mt-auto align-self-start');
   button.type = 'button'; button.addEventListener('click',()=>showDetail(book));
   body.append(button); card.append(image,body); column.append(card); results.append(column);
  }
 }
 async function search(page=1, newSearch=false) {
  if (newSearch) { currentQuery = input.value.trim(); currentField = field.value; }
  if (!currentQuery) { status.textContent='검색어를 입력해 주세요.';input.focus();return; }
  if (location.protocol === 'file:') {
   status.textContent = 'run.bat으로 서버를 시작한 뒤 안내된 주소에서 검색해 주세요.';
   return;
  }
  controller?.abort(); controller = new AbortController();
  const request = controller;
  const timeout = setTimeout(()=>request.abort(),20000);
  submit.disabled = true; previous.disabled = true; next.disabled = true;
  results.setAttribute('aria-busy','true'); status.textContent = '도서 정보를 불러오는 중입니다…';
  results.replaceChildren();pagination.hidden=true;
  try {
   const params = new URLSearchParams({field:currentField,q:currentQuery,page:String(page)});
   const response = await fetch('/api/books?'+params,{signal:request.signal});
   const contentType = response.headers.get('content-type') || '';
   if (!contentType.includes('application/json')) throw new Error('run.bat으로 서버를 시작한 뒤 안내된 주소에서 검색해 주세요.');
   const data = await response.json();
   if (!response.ok) throw new Error(data.error || '도서 정보를 불러오지 못했습니다.');
   currentPage = page;
   render(data.books);
   const pages = Math.max(1,Math.ceil(data.total/data.page_size));
   status.textContent = data.total ? `“${currentQuery}” 검색 결과 ${Number(data.total).toLocaleString()}건 · 국립중앙도서관` : '검색 결과가 없습니다. 다른 검색어나 ISBN을 입력해 주세요.';
   pageLabel.textContent = data.total ? `${page} / ${pages}` : '';
   pagination.hidden = !data.total;
   previous.disabled = page <= 1;
   next.disabled = page >= pages;
  } catch (error) {
   if (request !== controller) return;
   status.textContent = error.name === 'AbortError' ? '응답이 늦어지고 있습니다. 다시 검색해 주세요.' : error.message;
   pageLabel.textContent = '';
  } finally {
   clearTimeout(timeout);
   if (request === controller) { submit.disabled = false; results.setAttribute('aria-busy','false'); }
  }
 }
 form.addEventListener('submit',event=>{event.preventDefault();search(1,true);});
 previous.addEventListener('click',()=>search(currentPage-1));
 next.addEventListener('click',()=>search(currentPage+1));
 document.querySelectorAll('[data-book-query]').forEach(button=>button.addEventListener('click',()=>{
  field.value='title';input.value=button.dataset.bookQuery;
  document.getElementById('book-search').scrollIntoView({behavior:'smooth'});
  search(1,true);
 }));
 // 검색 제출 또는 도서 클릭 전에는 API를 호출하지 않습니다.
})();
