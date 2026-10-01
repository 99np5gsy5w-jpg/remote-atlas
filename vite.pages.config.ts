import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';
export default defineConfig({root:'web',base:'./',publicDir:'../public',plugins:[react()],resolve:{alias:{'@':path.resolve(import.meta.dirname)}},build:{outDir:'../pages-dist',emptyOutDir:true},server:{host:'127.0.0.1',port:5173}});
