export type Job = { id:string; company:string; companyId:string; title:string; description:string; location:string; countries:string[]; worldwide:boolean; restrictions:string[]; remoteType:string; remoteEvidence:string; level:string; levelSource:string; industry:string; department:string; employmentType:string; salary?:{min?:number;max?:number;currency?:string;interval?:string;text?:string;evidence?:string}|null; url:string; source:string; firstSeen:string; lastSeen:string; symbols:string[] };
export type Profile = { id:string; kind:'resume'|'cover'; name:string; text:string; uploadedAt:string; file?:Blob };
export type Filters = {query:string;location:string;level:string;industry:string;remote:string;currency:string;interval:string;salary:string;disclosed:boolean;employment:string;age:string};
export const initialFilters:Filters={query:'',location:'',level:'all',industry:'all',remote:'remote',currency:'USD',interval:'year',salary:'',disclosed:false,employment:'all',age:'all'};
export const skillTerms=['python','javascript','typescript','react','sql','java','golang','rust','aws','azure','kubernetes','docker','terraform','machine learning','data analysis','excel','tableau','power bi','salesforce','hubspot','customer success','account management','project management','product management','program management','financial analysis','accounting','nursing','clinical','marketing','seo','content strategy','copywriting','design','figma','user research','recruiting','human resources','compliance','risk management','cybersecurity','sales','leadership','operations','supply chain','procurement','customer support','technical writing','business development','communication','spanish','french','german','portuguese'];
export function extractSkills(text:string){return skillTerms.filter(t=>new RegExp('(?:^|[^a-z0-9])'+t+'(?:$|[^a-z0-9])','i').test(text));}
export function matchJob(j:Job,p:Profile[]){const have=extractSkills(p.map(x=>x.text).join('\n')),want=extractSkills(j.title+' '+j.description),shared=want.filter(s=>have.includes(s));return {score:want.length?Math.round(shared.length/want.length*100):0,shared,missing:want.filter(s=>!have.includes(s)).slice(0,6),available:p.length>0&&want.length>0};}
export function filterJobs(jobs:Job[],f:Filters){return jobs.filter(j=>{
  if(f.remote!=='all'&&j.remoteType!==f.remote)return false;
  if(f.query&&!f.query.toLowerCase().split(/\s+/).every(w=>(j.title+' '+j.company+' '+j.description).toLowerCase().includes(w)))return false;
  if(f.location&&!(j.location+' '+j.countries.join(' ')).toLowerCase().includes(f.location.toLowerCase())&&!j.worldwide)return false;
  if(f.level!=='all'&&j.level!==f.level)return false;
  if(f.industry!=='all'&&j.industry!==f.industry)return false;
  if(f.employment!=='all'&&!j.employmentType.toLowerCase().replaceAll('-',' ').includes(f.employment.toLowerCase()))return false;
  if(f.disclosed&&!j.salary)return false;
  if(f.salary&&(!j.salary||j.salary.currency!==f.currency||j.salary.interval!==f.interval||!Number.isFinite(j.salary.max)||Number(j.salary.max)<Number(f.salary)))return false;
  if(f.age!=='all'&&(Date.now()-Date.parse(j.firstSeen))/86400000>Number(f.age))return false;
  return true;
});}
export function salaryLabel(s:Job['salary']){if(!s)return 'Salary not disclosed';if(s.currency&&s.min!=null&&s.max!=null)return `${s.currency} ${Number(s.min).toLocaleString()} – ${Number(s.max).toLocaleString()}${s.interval?' / '+s.interval:''}`;return s.text||'See employer salary details';}
export function safeLink(s:string){try{const u=new URL(s);return ['https:','http:'].includes(u.protocol)?u.href:'#';}catch{return '#';}}
