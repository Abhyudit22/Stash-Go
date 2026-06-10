import './app.css'
import { mount } from 'svelte'
import App from './App.svelte'

// Securely target the root DOM container using Svelte 5 mounting mechanics
const app = mount(App, {
  target: document.getElementById('app')!,
})

export default app