import Icon from './Icon'
import PageHeader from './PageHeader'

export default function FeatureStub({ icon, title, description, bullets }) {
  return (
    <>
      <PageHeader icon={icon} title={title} subtitle={description} />
      <section className="stub-panel">
        <span className="stub-tag">Interface coming next</span>
        <h2>The engine is live and waiting</h2>
        <p>
          This feature is already served by the API. The interactive controls will be
          connected here in the next phase — the data pipeline behind it is complete.
        </p>
        <ul>
          {bullets.map((bullet) => (
            <li key={bullet}>{bullet}</li>
          ))}
        </ul>
      </section>
      <div className="stub-footnote">
        <Icon name="film" size={14} />
        Powered by 384-dimensional embeddings of every film&apos;s plot, genres, and themes.
      </div>
    </>
  )
}
