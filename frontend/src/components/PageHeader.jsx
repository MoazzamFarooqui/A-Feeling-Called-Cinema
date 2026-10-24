import Icon from './Icon'

export default function PageHeader({ icon, title, subtitle, children }) {
  return (
    <header className="page-header">
      <span className="page-header-icon">
        <Icon name={icon} size={22} />
      </span>
      <div className="page-header-text">
        <h1>{title}</h1>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {children && <div className="page-header-actions">{children}</div>}
    </header>
  )
}
