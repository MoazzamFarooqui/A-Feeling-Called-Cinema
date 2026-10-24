import Icon from './Icon'

export default function EmptyState({ icon = 'film', title, message, hint }) {
  return (
    <div className="empty-state">
      <span className="empty-icon">
        <Icon name={icon} size={22} />
      </span>
      <h3>{title}</h3>
      {message && <p>{message}</p>}
      {hint && <code className="empty-hint">{hint}</code>}
    </div>
  )
}
