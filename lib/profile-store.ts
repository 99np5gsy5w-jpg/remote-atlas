import type {Profile} from './jobs';
function db():Promise<IDBDatabase>{return new Promise((resolve,reject)=>{const r=indexedDB.open('remote-atlas-private-profile',1);r.onupgradeneeded=()=>r.result.createObjectStore('documents',{keyPath:'id'});r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});}
export async function readDocuments():Promise<Profile[]>{const d=await db();return new Promise((resolve,reject)=>{const tx=d.transaction('documents','readonly'),r=tx.objectStore('documents').getAll();r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);tx.oncomplete=()=>d.close();});}
export async function saveDocument(doc:Profile){const d=await db();return new Promise<void>((resolve,reject)=>{const tx=d.transaction('documents','readwrite');tx.objectStore('documents').put(doc);tx.oncomplete=()=>{d.close();resolve();};tx.onerror=()=>{d.close();reject(tx.error);};});}
export async function deleteDocument(id:string){const d=await db();return new Promise<void>((resolve,reject)=>{const tx=d.transaction('documents','readwrite');tx.objectStore('documents').delete(id);tx.oncomplete=()=>{d.close();resolve();};tx.onerror=()=>{d.close();reject(tx.error);};});}
export async function parseDocument(file:File):Promise<string>{
 if(file.size>5*1024*1024)throw new Error('Choose a file smaller than 5 MB.');
 const ext=file.name.split('.').pop()?.toLowerCase(),data=await file.arrayBuffer();let text='';
 if(ext==='txt')text=new TextDecoder('utf-8',{fatal:true}).decode(data);
 else if(ext==='docx'){const {unzipSync,strFromU8}=await import('fflate');const zip=unzipSync(new Uint8Array(data),{filter:f=>f.name==='word/document.xml'&&f.originalSize<2_000_000});if(!zip['word/document.xml'])throw new Error('Unable to read this Word file. Try a TXT export.');const xml=new DOMParser().parseFromString(strFromU8(zip['word/document.xml']),'application/xml');if(xml.querySelector('parsererror'))throw new Error('Malformed Word document.');text=Array.from(xml.getElementsByTagName('w:p')).map(p=>Array.from(p.getElementsByTagName('w:t')).map(t=>t.textContent).join('')).join('\n');}
 else if(ext==='pdf'){const pdfjs=await import('pdfjs-dist');pdfjs.GlobalWorkerOptions.workerSrc=new URL('pdfjs-dist/build/pdf.worker.min.mjs',import.meta.url).toString();const task=pdfjs.getDocument({data});const pdf=await task.promise;try{if(pdf.numPages>30)throw new Error('Choose a document with 30 pages or fewer.');for(let i=1;i<=pdf.numPages;i++){const p=await pdf.getPage(i),c=await p.getTextContent();text+=c.items.map(x=>'str' in x?x.str:'').join(' ')+'\n';}}finally{await task.destroy();}}
 else throw new Error('Choose a PDF, DOCX, or TXT file.');
 if(text.trim().length<40)throw new Error('No readable text found. Scanned PDFs need OCR first; try a text-based PDF, DOCX, or TXT file.');
 if(text.length>150000)throw new Error('Please use a shorter resume or cover letter.');return text.trim();
}
