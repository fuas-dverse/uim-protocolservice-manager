import { Router, Route, A } from '@solidjs/router';
import Home from './pages/Home';
import Services from './pages/Services';
import Intents from './pages/Intents';
import './style.css';

function App() {
  return (
    <Router>
      <Route path="/" component={Home} />
      <Route path="/services" component={Services} />
      <Route path="/intents" component={Intents} />
    </Router>
  );
}

export default App;