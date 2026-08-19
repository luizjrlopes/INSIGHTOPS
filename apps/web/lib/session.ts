import type {Session} from "./types";
const KEY="insightops_session";
export const getSession=():Session|null=>{if(typeof window==='undefined')return null;try{return JSON.parse(localStorage.getItem(KEY)||'null')}catch{return null}};
export const setSession=(s:Session|null)=>{if(typeof window==='undefined')return;s?localStorage.setItem(KEY,JSON.stringify(s)):localStorage.removeItem(KEY)};
