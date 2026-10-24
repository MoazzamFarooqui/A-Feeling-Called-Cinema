import { Link, NavLink, Outlet } from 'react-router-dom'
import { FEATURES } from '../features'
import Icon from './Icon'

export default function Layout() {
  const linkClass = ({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link to="/" className="brand">
          <span className="brand-mark">
            <Icon name="film" size={19} />
          </span>
          <span className="brand-name">
            A Feeling Called <em>Cinema</em>
          </span>
        </Link>

        <nav className="side-nav" aria-label="Main navigation">
          <NavLink to="/" end className={linkClass}>
            <Icon name="home" size={18} />
            Discover
          </NavLink>
          {FEATURES.map((feature) => (
            <NavLink key={feature.path} to={feature.path} className={linkClass}>
              <Icon name={feature.icon} size={18} />
              {feature.nav}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <p>25,706 films · 1920s–2020s</p>
          <p>Built with FastAPI + React</p>
        </div>
      </aside>

      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}
