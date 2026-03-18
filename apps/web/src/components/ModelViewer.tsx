import { useRef, useState, CSSProperties } from 'react'
// @ts-ignore — model-viewer ships its own types; we declare the custom element below
import '@google/model-viewer'

// Extend JSX to include the <model-viewer> web component
declare global {
  namespace JSX {
    interface IntrinsicElements {
      'model-viewer': React.DetailedHTMLProps<
        React.HTMLAttributes<HTMLElement> & {
          src?: string
          alt?: string
          'camera-controls'?: boolean | string
          'auto-rotate'?: boolean | string
          'shadow-intensity'?: string
          'loading'?: string
          poster?: string
          ar?: boolean | string
          style?: CSSProperties
        },
        HTMLElement
      >
    }
  }
}

interface ModelViewerProps {
  /** URL or path to the .glb / .gltf file */
  src: string
  /** Accessible alt text */
  alt?: string
  /** Inline styles applied to the model-viewer element */
  style?: CSSProperties
  /** Optional poster image shown while loading */
  poster?: string
}

type LoadState = 'loading' | 'loaded' | 'error'

export default function ModelViewer({
  src,
  alt = '3D garment model',
  style,
  poster,
}: ModelViewerProps) {
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const viewerRef = useRef<HTMLElement>(null)

  const baseStyle: CSSProperties = {
    width: '100%',
    height: '480px',
    background: '#1a1a1a',
    borderRadius: '12px',
    display: 'block',
    position: 'relative',
    ...style,
  }

  return (
    <div style={{ position: 'relative', display: 'inline-block', width: style?.width ?? '100%' }}>
      {/* Loading spinner */}
      {loadState === 'loading' && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10,
            pointerEvents: 'none',
          }}
        >
          <Spinner />
        </div>
      )}

      {/* Error state */}
      {loadState === 'error' && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#1a1a1a',
            borderRadius: '12px',
            color: '#ff6b6b',
            gap: '0.5rem',
            zIndex: 10,
          }}
        >
          <span style={{ fontSize: '2rem' }}>⚠️</span>
          <span style={{ fontSize: '0.9rem' }}>Failed to load 3D model</span>
          <code style={{ fontSize: '0.75rem', opacity: 0.6 }}>{src}</code>
        </div>
      )}

      <model-viewer
        ref={viewerRef}
        src={src}
        alt={alt}
        poster={poster}
        camera-controls
        auto-rotate
        shadow-intensity="1.2"
        loading="eager"
        style={{
          ...baseStyle,
          visibility: loadState === 'error' ? 'hidden' : 'visible',
        }}
        onLoad={() => setLoadState('loaded')}
        onError={() => setLoadState('error')}
      />
    </div>
  )
}

// ── Inline spinner — no extra deps ───────────────────────────────────────────
function Spinner() {
  return (
    <svg
      width="48"
      height="48"
      viewBox="0 0 48 48"
      style={{ animation: 'spin 0.9s linear infinite' }}
    >
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <circle
        cx="24"
        cy="24"
        r="20"
        fill="none"
        stroke="#ffffff33"
        strokeWidth="4"
      />
      <circle
        cx="24"
        cy="24"
        r="20"
        fill="none"
        stroke="#ffffff"
        strokeWidth="4"
        strokeDasharray="30 100"
        strokeLinecap="round"
      />
    </svg>
  )
}
