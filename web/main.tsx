import React from 'react';
import {createRoot} from 'react-dom/client';
import RemoteAtlas from '../app/client';
import '../app/globals.css';
createRoot(document.getElementById('root')!).render(<React.StrictMode><RemoteAtlas/></React.StrictMode>);
