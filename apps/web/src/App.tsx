import ModelViewer from './components/ModelViewer'

// Official Google model-viewer astronaut demo .glb
const DEMO_GLB =
  'https://modelviewer.dev/shared-assets/models/Astronaut.glb'

export default function App() {
  return (
    <div style={{ padding: '2rem' }}>
      <h1 style={{ marginBottom: '1.5rem', fontSize: '1.4rem', letterSpacing: '0.05em' }}>
        Fashion Tech — 3D Viewer
      </h1>
      <ModelViewer
        src={DEMO_GLB}
        alt="Astronaut demo model"
        style={{ width: '100%', maxWidth: '600px', height: '500px' }}
      />
    </div>
  )
}
