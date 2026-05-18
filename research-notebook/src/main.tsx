import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './app/App';
import './shared/design-system/tokens.css';
import './shared/design-system/global.css';
import './shared/components/state-block.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
