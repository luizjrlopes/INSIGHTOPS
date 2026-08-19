import {getSession} from "./session";
const BASE=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000";
export async function api<T=any>(path:string,init:RequestInit={}):Promise<T>{const s=getSession();const headers=new Headers(init.headers);if(s)headers.set('Authorization',`Bearer ${s.token}`);if(init.body&&!(init.body instanceof FormData))headers.set('Content-Type','application/json');const r=await fetch(BASE+path,{...init,headers});if(!r.ok)throw new Error((await r.text())||`HTTP ${r.status}`);const type=r.headers.get('content-type')||'';return type.includes('application/json')?r.json() as Promise<T>:r.text() as Promise<T>}
export {BASE};
