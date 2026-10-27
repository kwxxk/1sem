(() => {
 const feed=document.querySelector('[data-thread-feed]'),related=document.getElementById('relatedThreads');if(!feed&&!related)return;
 const api=(...args)=>ThreadAPI.request(...args),compose=document.getElementById('composeModal'),reader=document.getElementById('threadReadModal');
 const form=document.getElementById('composeForm'),bookField=document.getElementById('threadBook'),titleField=document.getElementById('threadTitle'),bodyField=document.getElementById('threadBody'),status=document.getElementById('composeStatus');
 const notice=document.getElementById(feed?'mainThreadNotice':'threadNotice');
 let page=1,current=[],editing=null,reading=null,bookISBN='',generation=0;
 function el(tag,value,className){const node=document.createElement(tag);node.textContent=value;if(className)node.className=className;return node;}
 function sort(){return document.getElementById('threadSort')?.value||'latest';}
 function examples(){return document.getElementById('threadExamples')?.checked?'1':'0';}
 function context(){return related?window.ThreadBook||{}:{};}
 async function load(){
  const id=++generation;notice.textContent='쓰레드를 불러오는 중입니다…';
  try{
   const book=context(),q=new URLSearchParams({page:String(page),sort:sort(),examples:examples()});if(related){q.set('isbn',book.isbn||'');q.set('title',book.title||'');}
   const data=await api('/api/posts?'+q);if(id!==generation)return;
   if(!data.posts.length&&page>1){page--;return load();}current=data.posts;render(data.total);notice.textContent='';
  }catch(e){if(id===generation)notice.textContent=e.message;}
 }
 function openRead(post,deleting=false){reading=post;document.getElementById('readThreadTitle').textContent=post.title;document.getElementById('readThreadMeta').textContent=post.author+' · '+post.bookTitle+(post.sample?' · 예시':'');document.getElementById('readThreadBody').textContent=post.body;document.getElementById('readEdit').hidden=!post.is_owner;document.getElementById('readDelete').hidden=!post.is_owner;document.getElementById('deletePanel').hidden=!deleting;document.getElementById('readStatus').textContent='';updateLike();bootstrap.Modal.getOrCreateInstance(reader).show();}
 function updateLike(){const button=document.getElementById('readLike');button.textContent=(reading.liked?'좋아요 취소':'좋아요')+' '+reading.likes;button.setAttribute('aria-pressed',String(reading.liked));}
 function card(post){
  const column=el('div','','col-12 col-sm-4'),article=el('article','','card thread-card h-100'),image=document.createElement('img');image.className='card-img-top';image.src='assets/threads/img'+((Number(post.id)-1)%6+1)+'.jpg';image.alt='';image.loading='lazy';
  const body=el('div','','card-body'),heading=el('h3','','card-title'),button=el('button',post.title,'thread-open');button.type='button';button.addEventListener('click',()=>openRead(post));heading.append(button);body.append(heading,el('p',post.body,'card-text thread-excerpt'));
  const footer=el('div',post.author,'card-footer');if(post.sample)footer.append(el('span','예시','badge text-bg-secondary ms-2'));if(post.is_owner)footer.append(el('span','내 글','badge text-bg-light ms-2'));footer.append(el('span',post.bookTitle,'book-name'),el('span','좋아요 '+post.likes,'small d-block mt-1'));article.append(image,body,footer);column.append(article);return column;
 }
 function render(total){
  const pages=Math.max(1,Math.ceil(total/3));
  if(feed){feed.replaceChildren();const row=el('div','','row g-4 thread-page');row.dataset.threadPage=String(page);current.forEach(post=>row.append(card(post)));feed.append(row);if(!current.length)feed.append(el('p','아직 글이 없습니다. 첫 이야기를 남겨보세요.','text-secondary py-4'));
   const list=document.getElementById('threadPagination');list.replaceChildren();const start=Math.max(1,Math.min(page-2,pages-4));
   const entries=[...(page>1?[['이전',page-1]]:[]),...Array.from({length:Math.min(5,pages)},(_,i)=>[String(start+i),start+i]),...(page<pages?[['다음',page+1]]:[])];
   for(const[label,n]of entries){const li=el('li','','page-item'+(n===page&&label===String(n)?' active':'')),button=el('button',label,'page-link');button.type='button';button.dataset.page=String(n);if(n===page&&label===String(n))button.setAttribute('aria-current','page');button.addEventListener('click',()=>{page=n;load();});li.append(button);list.append(li);}list.parentElement.hidden=total===0;document.getElementById('page-status').textContent=page+'페이지';
  }else{
   related.replaceChildren();for(const post of current){const item=el('li','','list-group-item'),h=el('h3','','fs-6'),button=el('button',post.title,'thread-open');button.type='button';button.addEventListener('click',()=>openRead(post));h.append(button);item.append(h,el('p',post.body,'small thread-excerpt'),el('div',post.author+' · 좋아요 '+post.likes+(post.sample?' · 예시':''),'small text-secondary'));related.append(item);}if(!current.length)related.append(el('li','이 책의 첫 쓰레드를 남겨보세요.','list-group-item text-secondary'));
   document.getElementById('relatedPage').textContent=page+' / '+pages;document.getElementById('relatedPrevious').disabled=page<=1;document.getElementById('relatedNext').disabled=page>=pages;
  }
 }
 function open(book,post=null){ThreadAuth.requireLogin(()=>{editing=post;form.reset();const ctx=book||context();bookField.value=post?.bookTitle||ctx.bookTitle||ctx.title||'';bookISBN=post?.isbn||ctx.isbn||'';bookField.readOnly=!!post||!!related;titleField.value=post?.title||'';bodyField.value=post?.body||'';document.getElementById('composeTitle').textContent=post?'쓰레드 수정':'쓰레드 작성';status.textContent='';bootstrap.Modal.getOrCreateInstance(compose).show();});}
 function afterRead(action){reader.addEventListener('hidden.bs.modal',action,{once:true});bootstrap.Modal.getOrCreateInstance(reader).hide();}
 window.ThreadComposer={open,edit:post=>open(null,post),read:openRead,refresh:load};
 document.getElementById('writeThread').addEventListener('click',()=>open());
 compose.addEventListener('shown.bs.modal',()=>{(bookField.value?titleField:bookField).focus();});bookField.addEventListener('input',()=>{bookISBN='';});
 form.addEventListener('submit',async event=>{
  event.preventDefault();for(const field of[bookField,titleField,bodyField])if(!field.value.trim()){status.textContent='관련 도서, 제목, 내용을 모두 입력해 주세요.';field.focus();return;}
  const submit=form.querySelector('[type=submit]');submit.disabled=true;
  try{const body={title:titleField.value.trim(),body:bodyField.value.trim(),bookTitle:bookField.value.trim(),isbn:bookISBN};await api(editing?'/api/posts/'+editing.id:'/api/posts',body,editing?'PATCH':'POST');page=1;await load();bootstrap.Modal.getOrCreateInstance(compose).hide();window.dispatchEvent(new CustomEvent('thread:datachange'));notice.textContent=editing?'쓰레드를 수정했습니다.':'쓰레드를 등록했습니다. 같은 서버의 다른 사용자도 읽을 수 있습니다.';form.reset();}
  catch(e){status.textContent=e.message;}finally{submit.disabled=false;}
 });
 document.getElementById('readEdit').addEventListener('click',()=>afterRead(()=>open(null,reading)));
 document.getElementById('readDelete').addEventListener('click',()=>{document.getElementById('deletePanel').hidden=false;});document.getElementById('cancelDelete').addEventListener('click',()=>{document.getElementById('deletePanel').hidden=true;});
 document.getElementById('confirmDelete').addEventListener('click',async()=>{const button=document.getElementById('confirmDelete');button.disabled=true;try{await api('/api/posts/'+reading.id,{},'DELETE');bootstrap.Modal.getOrCreateInstance(reader).hide();await load();window.dispatchEvent(new CustomEvent('thread:datachange'));notice.textContent='글을 삭제했습니다.';}catch(e){document.getElementById('readStatus').textContent=e.message;}finally{button.disabled=false;}});
 async function like(){const button=document.getElementById('readLike');button.disabled=true;try{const data=await api('/api/posts/'+reading.id+'/like',{liked:!reading.liked});reading.likes=data.likes;reading.liked=data.liked;updateLike();load();}catch(e){document.getElementById('readStatus').textContent=e.message;}finally{button.disabled=false;}}
 document.getElementById('readLike').addEventListener('click',()=>{if(ThreadAuth.getUser())like();else afterRead(()=>ThreadAuth.requireLogin(()=>{reading.is_owner=false;openRead(reading);like();}));});
 if(related){document.getElementById('relatedPrevious').addEventListener('click',()=>{page--;load();});document.getElementById('relatedNext').addEventListener('click',()=>{page++;load();});}
 document.getElementById('refreshThreads').addEventListener('click',load);
 document.getElementById('threadSort').addEventListener('change',()=>{page=1;load();});document.getElementById('threadExamples').addEventListener('change',()=>{page=1;load();});
 window.addEventListener('thread:authchange',load);window.addEventListener('thread:bookready',()=>{page=1;load();});window.addEventListener('focus',load);
 ThreadAPI.ready.then(load);
})();
