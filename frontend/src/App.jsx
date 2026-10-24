import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import MoodToScene from './pages/MoodToScene'
import WatchParty from './pages/WatchParty'
import TimeBudget from './pages/TimeBudget'
import DoubleFeature from './pages/DoubleFeature'
import CulturalBridge from './pages/CulturalBridge'
import EraMachine from './pages/EraMachine'
import HiddenGems from './pages/HiddenGems'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/mood" element={<MoodToScene />} />
          <Route path="/watch-party" element={<WatchParty />} />
          <Route path="/time-budget" element={<TimeBudget />} />
          <Route path="/double-feature" element={<DoubleFeature />} />
          <Route path="/cultural-bridge" element={<CulturalBridge />} />
          <Route path="/era-machine" element={<EraMachine />} />
          <Route path="/hidden-gems" element={<HiddenGems />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
