// 개별 필수 예제 페이지의 정적 pagination.
if(!document.querySelector('[data-thread-feed]'))document.querySelectorAll('[data-page]').forEach(button=>button.addEventListener('click',()=>{
 document.querySelectorAll('[data-thread-page]').forEach(group=>{group.hidden=group.dataset.threadPage!==button.dataset.page;});
 document.querySelectorAll('[data-page]').forEach(item=>{const active=item===button;item.parentElement.classList.toggle('active',active);if(active)item.setAttribute('aria-current','page');else item.removeAttribute('aria-current');});
 document.getElementById('page-status').textContent=button.dataset.page+'페이지';
}));
window.ThreadBooks={url(book){return '07-book_detail.html?'+new URLSearchParams({isbn:book.isbn||'',title:book.title||book.bookTitle||'',author:book.author||''});}};
(() => {
 let user=null,csrf='',pending=null,success=false;
 let resolveReady;const ready=new Promise(resolve=>{resolveReady=resolve;});
 function element(tag,value,className){const el=document.createElement(tag);el.textContent=value;if(className)el.className=className;return el;}
 async function request(path,body,method='POST'){
  await ready;
  const options={credentials:'same-origin',headers:{'X-Thread-Request':'1'}};
  if(body!==undefined){options.method=method;options.headers['Content-Type']='application/json';options.headers['X-CSRF-Token']=csrf;options.body=JSON.stringify(body);}
  let response,data;
  try{response=await fetch(path,options);data=await response.json();}catch(_){throw new Error('서버에 연결하지 못했습니다. run.bat 실행 상태를 확인해 주세요.');}
  if(!response.ok){const error=new Error(data.error||'요청을 완료하지 못했습니다.');error.status=response.status;throw error;}
  return data;
 }
 window.ThreadAPI={request,ready};
 const auth=document.getElementById('authButton');
 if(!auth){resolveReady();return;}
 const login=document.getElementById('loginModal'),form=document.getElementById('loginForm'),nickname=document.getElementById('nickname'),password=document.getElementById('loginPassword'),error=document.getElementById('loginError');
 const profile=document.getElementById('myPageModal');
 function render(){
  auth.textContent=user?'로그아웃':'로그인';auth.dataset.bsTarget=user?'#logoutModal':'#loginModal';
  document.getElementById('profileNickname').textContent=user?.username||'';
  document.getElementById('profileAccountType').textContent=user?.guest?'체험 계정입니다. 로그아웃 후 같은 계정으로 돌아오려면 회원가입을 이용해 주세요.':'내 글과 관심 도서는 계정에 저장됩니다.';
  document.getElementById('upgradeAccount').hidden=!user?.guest;
  window.dispatchEvent(new CustomEvent('thread:authchange'));
 }
 async function authenticate(mode){
  const buttons=[...form.querySelectorAll('button')];buttons.forEach(button=>button.disabled=true);error.textContent='';
  try{
   const data=await request('/api/auth/'+mode,mode==='guest'?{}:{username:nickname.value.trim(),password:password.value});
   user=data.user;csrf=data.csrf;success=true;render();bootstrap.Modal.getOrCreateInstance(login).hide();
   document.getElementById('auth-status').textContent=user.username+'님, 로그인했습니다.';
  }catch(e){error.textContent=e.message;}finally{buttons.forEach(button=>button.disabled=false);}
 }
 form.addEventListener('submit',event=>{event.preventDefault();authenticate(document.getElementById('authMode').value);});
 document.getElementById('guestLogin').addEventListener('click',()=>authenticate('guest'));
 document.getElementById('authMode').addEventListener('change',event=>{password.autocomplete=event.target.value==='register'?'new-password':'current-password';error.textContent='';});
 login.addEventListener('shown.bs.modal',()=>nickname.focus());
 login.addEventListener('hidden.bs.modal',()=>{form.reset();error.textContent='';const action=success?pending:null;pending=null;success=false;if(action)action();});
 window.ThreadAuth={getNickname:()=>user?.username||'',getUser:()=>user,async requireLogin(action){await ready;if(user){action();return;}pending=action;bootstrap.Modal.getOrCreateInstance(login).show();}};
 document.getElementById('confirmLogout').addEventListener('click',async()=>{
  try{await request('/api/auth/logout',{});user=null;csrf='';render();bootstrap.Modal.getOrCreateInstance(document.getElementById('logoutModal')).hide();document.getElementById('auth-status').textContent='로그아웃했습니다.';}
  catch(e){document.getElementById('logoutError').textContent=e.message;}
 });
 function legacyPosts(){
  try{const a=JSON.parse(sessionStorage.getItem('thread-posts-v1')||'[]'),b=JSON.parse(sessionStorage.getItem('thread-own-9788936433598')||'[]');return[...(Array.isArray(a)?a:[]),...(Array.isArray(b)?b.map(item=>({...item,bookTitle:'채식주의자',isbn:'9788936433598'})):[])].filter(post=>post&&typeof post.title==='string'&&typeof post.body==='string'&&typeof post.bookTitle==='string').slice(0,100);}catch(_){return[];}
 }
 let profilePage=1;
 async function loadProfile(){
  document.getElementById('legacyImportBox').hidden=legacyPosts().length===0;
  const list=document.getElementById('myPosts'),books=document.getElementById('mySavedBooks'),status=document.getElementById('profileStatus');
  list.replaceChildren();books.replaceChildren();status.textContent='내 기록을 불러오는 중입니다…';
  try{
   const [posts,saved]=await Promise.all([request('/api/posts?mine=1&examples=0&page='+profilePage),request('/api/bookmarks')]);
   if(!posts.posts.length&&profilePage>1){profilePage--;return loadProfile();}
   for(const post of posts.posts){
    const item=element('li','','list-group-item'),details=document.createElement('details'),summary=element('summary',post.title),body=element('p',post.body,'thread-full-body mt-2 small');details.append(summary,body);item.append(details,element('p',post.bookTitle,'small text-secondary mb-2'));
    if(window.ThreadComposer){for(const [label,action]of [['수정',()=>window.ThreadComposer.edit(post)],['삭제',()=>window.ThreadComposer.read(post,true)]]){const button=element('button',label,'btn btn-outline-secondary btn-sm me-2');button.type='button';button.addEventListener('click',()=>{profile.addEventListener('hidden.bs.modal',action,{once:true});bootstrap.Modal.getOrCreateInstance(profile).hide();});item.append(button);}}
    list.append(item);
   }
   if(!posts.posts.length)list.append(element('li','작성한 글이 없습니다.','list-group-item text-secondary'));
   document.getElementById('myPostPage').textContent=profilePage+' / '+Math.max(1,Math.ceil(posts.total/3));
   document.getElementById('myPostPrevious').disabled=profilePage<=1;document.getElementById('myPostNext').disabled=profilePage*3>=posts.total;
   for(const book of saved.books){const item=element('li','','list-group-item d-flex align-items-center justify-content-between gap-2'),link=element('a',book.title);link.href=ThreadBooks.url(book);const remove=element('button','빼기','btn btn-outline-secondary btn-sm');remove.type='button';remove.addEventListener('click',async()=>{try{await request('/api/bookmarks/'+encodeURIComponent(book.key),{},'DELETE');window.dispatchEvent(new CustomEvent('thread:bookmarkschange'));loadProfile();}catch(e){status.textContent=e.message;}});item.append(link,remove);books.append(item);}
   if(!saved.books.length)books.append(element('li','담은 책이 없습니다.','list-group-item text-secondary'));
   status.textContent='';
  }catch(e){status.textContent=e.message;}
 }
 const myButton=document.getElementById('myPageButton');myButton.removeAttribute('data-bs-toggle');myButton.removeAttribute('data-bs-target');
 document.querySelectorAll('[data-open-profile]').forEach(button=>button.addEventListener('click',()=>myButton.click()));
 myButton.addEventListener('click',()=>ThreadAuth.requireLogin(()=>{profilePage=1;bootstrap.Modal.getOrCreateInstance(profile).show();}));
 document.getElementById('importLegacyPosts').addEventListener('click',async()=>{
  const button=document.getElementById('importLegacyPosts'),status=document.getElementById('profileStatus');button.disabled=true;
  try{
   const track='thread-imported-'+user.id;let imported=[];try{imported=JSON.parse(sessionStorage.getItem(track)||'[]');if(!Array.isArray(imported))imported=[];}catch(_){}
   let count=0;
   for(const [i,post] of legacyPosts().entries()){
    const id=post.id||String(i);if(imported.includes(id))continue;
    await request('/api/posts',{title:post.title.slice(0,100),body:post.body.slice(0,2000),bookTitle:post.bookTitle.slice(0,200),isbn:/^(?:[0-9]{13}|[0-9]{9}[0-9X])$/.test(post.isbn||'')?post.isbn:''});
    imported.push(id);try{sessionStorage.setItem(track,JSON.stringify(imported));}catch(_){}count++;
   }
   await loadProfile();status.textContent=count+'개의 이전 체험 글을 현재 계정으로 가져왔습니다.';window.ThreadComposer?.refresh?.();
  }catch(e){status.textContent=e.message;}finally{button.disabled=false;}
 });
 profile.addEventListener('shown.bs.modal',loadProfile);
 document.getElementById('upgradeAccount').addEventListener('click',()=>{profile.addEventListener('hidden.bs.modal',()=>{document.getElementById('authMode').value='register';bootstrap.Modal.getOrCreateInstance(login).show();},{once:true});bootstrap.Modal.getOrCreateInstance(profile).hide();});
 document.getElementById('myPostPrevious').addEventListener('click',()=>{profilePage--;loadProfile();});document.getElementById('myPostNext').addEventListener('click',()=>{profilePage++;loadProfile();});
 window.addEventListener('thread:datachange',()=>{if(profile.classList.contains('show'))loadProfile();});
 (async()=>{
  try{if(location.protocol==='file:')throw new Error();const response=await fetch('/api/session',{credentials:'same-origin'});if(!response.ok)throw new Error();const data=await response.json();user=data.user;csrf=data.csrf||'';}
  catch(_){document.getElementById('auth-status').textContent='로그인과 글쓰기를 사용하려면 run.bat으로 서버를 실행해 주세요.';}
  finally{resolveReady();render();}
 })();
})();
