# Outfit Builder Specification — Fashion Tech MVP

**Author:** Frontend Engineer  
**Date:** 2026-03-17  
**Component:** OutfitBuilder UI + Related Components  
**Status:** Design Document

---

## Overview

The Outfit Builder is the user-facing interface for:
1. **Browsing garments** (search, filter, preview)
2. **Building outfits** (add/remove/swap garments)
3. **Viewing fit information** (sizing, measurements, how it fits)
4. **Saving and managing outfits**
5. **Purchasing** (links to retail partners)

It's a **sidebar interface** paired with the 3D viewport, designed for discoverability and quick decision-making.

---

## UI Layout

### High-Level Structure

```
┌─────────────────────────────────────────────────────────┐
│                      HEADER                              │
│  Logo          [Outfit Name Input]     [User Menu]      │
├─────────────────────────────┬──────────────────────────┤
│                             │                           │
│                             │    SIDEBAR                │
│      VIEWPORT (3D)          │    ┌─────────────────┐    │
│                             │    │ GARMENT SELECTOR│    │
│                             │    │  [Search Box]   │    │
│                             │    │  [Category Tabs]│    │
│                             │    │  [Grid of Items]│    │
│    + Animation Controls     │    └─────────────────┘    │
│                             │    ┌─────────────────┐    │
│                             │    │ OUTFIT BUILDER  │    │
│                             │    │ [Current Items] │    │
│                             │    │ [Save Button]   │    │
│                             │    └─────────────────┘    │
│                             │    ┌─────────────────┐    │
│                             │    │ SIZE CHART      │    │
│                             │    │ [Fit Info]      │    │
│                             │    │ [Buy Links]     │    │
│                             │    └─────────────────┘    │
└─────────────────────────────┴──────────────────────────┘
```

---

## Components

### 1. **GarmentSelector** — Browse and Select Garments

```typescript
interface GarmentSelectorProps {
  garments: Garment[]
  selectedGarments: Garment[]
  onGarmentAdd: (garment: Garment) => void
  onGarmentRemove: (garmentId: string) => void
  onGarmentHover?: (garmentId: string | null) => void
}

export const GarmentSelector: React.FC<GarmentSelectorProps> = ({
  garments,
  selectedGarments,
  onGarmentAdd,
  onGarmentRemove,
  onGarmentHover,
}) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedColor, setSelectedColor] = useState<string | null>(null)

  // Filter garments based on search + category + color
  const filteredGarments = useMemo(() => {
    return garments.filter((g) => {
      const matchesSearch =
        g.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        g.brand.toLowerCase().includes(searchQuery.toLowerCase())

      const matchesCategory = !selectedCategory || g.category === selectedCategory
      const matchesColor = !selectedColor || g.color.includes(selectedColor)

      return matchesSearch && matchesCategory && matchesColor
    })
  }, [garments, searchQuery, selectedCategory, selectedColor])

  const isSelected = (garmentId: string) =>
    selectedGarments.some((g) => g.id === garmentId)

  return (
    <div className="flex flex-col gap-4 p-4 border-t">
      <h2 className="text-lg font-semibold">Garments</h2>

      {/* Search Box */}
      <input
        type="text"
        placeholder="Search by name or brand..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-black"
      />

      {/* Category Filter */}
      <div className="flex gap-2 flex-wrap">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() =>
              setSelectedCategory(selectedCategory === cat ? null : cat)
            }
            className={`px-3 py-1 rounded-full text-xs font-medium transition ${
              selectedCategory === cat
                ? 'bg-black text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Color Filter */}
      <div className="flex gap-2 flex-wrap">
        {COLORS.map((color) => (
          <button
            key={color}
            onClick={() =>
              setSelectedColor(selectedColor === color ? null : color)
            }
            className={`w-6 h-6 rounded-full border-2 transition ${
              selectedColor === color
                ? 'border-black scale-110'
                : 'border-gray-300'
            }`}
            style={{ backgroundColor: color }}
            title={color}
          />
        ))}
      </div>

      {/* Garment Grid */}
      <div className="grid grid-cols-2 gap-3 overflow-y-auto max-h-96">
        {filteredGarments.map((garment) => (
          <GarmentCard
            key={garment.id}
            garment={garment}
            isSelected={isSelected(garment.id)}
            onAdd={() => onGarmentAdd(garment)}
            onRemove={() => onGarmentRemove(garment.id)}
            onHover={() => onGarmentHover?.(garment.id)}
            onUnhover={() => onGarmentHover?.(null)}
          />
        ))}
      </div>

      {filteredGarments.length === 0 && (
        <p className="text-center text-gray-500 text-sm">No garments found</p>
      )}
    </div>
  )
}
```

### 1b. **GarmentCard** — Individual Garment Preview

```typescript
interface GarmentCardProps {
  garment: Garment
  isSelected: boolean
  onAdd: () => void
  onRemove: () => void
  onHover: () => void
  onUnhover: () => void
}

export const GarmentCard: React.FC<GarmentCardProps> = ({
  garment,
  isSelected,
  onAdd,
  onRemove,
  onHover,
  onUnhover,
}) => {
  return (
    <div
      onMouseEnter={onHover}
      onMouseLeave={onUnhover}
      className={`flex flex-col gap-2 p-3 rounded-lg border-2 transition cursor-pointer ${
        isSelected
          ? 'border-black bg-gray-100'
          : 'border-gray-200 hover:border-gray-400'
      }`}
    >
      {/* Thumbnail */}
      <img
        src={garment.thumbnailUrl}
        alt={garment.name}
        className="w-full aspect-square object-cover rounded"
      />

      {/* Info */}
      <div className="flex flex-col gap-1">
        <h3 className="font-semibold text-sm truncate">{garment.name}</h3>
        <p className="text-xs text-gray-600">{garment.brand}</p>
        <p className="text-xs font-semibold">{`£${garment.price}`}</p>
      </div>

      {/* Button */}
      <button
        onClick={(e) => {
          e.stopPropagation()
          isSelected ? onRemove() : onAdd()
        }}
        className={`py-2 rounded font-medium text-xs transition ${
          isSelected
            ? 'bg-red-100 text-red-700 hover:bg-red-200'
            : 'bg-black text-white hover:bg-gray-800'
        }`}
      >
        {isSelected ? '✓ Remove' : '+ Add'}
      </button>
    </div>
  )
}
```

---

### 2. **OutfitBuilder** — Current Outfit Display & Management

```typescript
interface OutfitBuilderProps {
  selectedGarments: Garment[]
  onGarmentRemove: (garmentId: string) => void
  onGarmentSwap: (garmentId: string, newGarment: Garment) => void
  onSaveOutfit: (outfitName: string) => void
  isSaved?: boolean
}

export const OutfitBuilder: React.FC<OutfitBuilderProps> = ({
  selectedGarments,
  onGarmentRemove,
  onGarmentSwap,
  onSaveOutfit,
  isSaved = false,
}) => {
  const [outfitName, setOutfitName] = useState('My Outfit')
  const [showSaveModal, setShowSaveModal] = useState(false)
  const [swappingGarmentId, setSwappingGarmentId] = useState<string | null>(null)

  const handleSave = () => {
    onSaveOutfit(outfitName)
    setShowSaveModal(false)
  }

  return (
    <div className="flex flex-col gap-4 p-4 border-t">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Your Outfit</h2>
        {isSaved && <span className="text-xs text-green-600">✓ Saved</span>}
      </div>

      {/* Outfit Items */}
      {selectedGarments.length === 0 ? (
        <p className="text-center text-gray-500 text-sm py-4">
          Add garments to your outfit
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {selectedGarments.map((garment, index) => (
            <OutfitItem
              key={garment.id}
              garment={garment}
              index={index}
              onRemove={() => onGarmentRemove(garment.id)}
              onSwap={() => setSwappingGarmentId(garment.id)}
            />
          ))}
        </div>
      )}

      {/* Save Button */}
      {selectedGarments.length > 0 && (
        <button
          onClick={() => setShowSaveModal(true)}
          className="w-full py-2 bg-black text-white rounded font-semibold hover:bg-gray-800 transition"
        >
          {isSaved ? '✓ Update Outfit' : '💾 Save Outfit'}
        </button>
      )}

      {/* Save Modal */}
      {showSaveModal && (
        <SaveOutfitModal
          outfitName={outfitName}
          onNameChange={setOutfitName}
          onSave={handleSave}
          onCancel={() => setShowSaveModal(false)}
        />
      )}
    </div>
  )
}
```

### 2b. **OutfitItem** — Individual Item in Current Outfit

```typescript
interface OutfitItemProps {
  garment: Garment
  index: number
  onRemove: () => void
  onSwap: () => void
}

export const OutfitItem: React.FC<OutfitItemProps> = ({
  garment,
  index,
  onRemove,
  onSwap,
}) => {
  return (
    <div className="flex gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
      {/* Thumbnail */}
      <img
        src={garment.thumbnailUrl}
        alt={garment.name}
        className="w-16 h-16 object-cover rounded"
      />

      {/* Info */}
      <div className="flex-1 flex flex-col justify-between">
        <div>
          <h4 className="font-semibold text-sm">{garment.name}</h4>
          <p className="text-xs text-gray-600">{garment.brand}</p>
        </div>
        <p className="text-sm font-semibold">£{garment.price}</p>
      </div>

      {/* Actions */}
      <div className="flex flex-col gap-1">
        <button
          onClick={onSwap}
          className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition"
        >
          Swap
        </button>
        <button
          onClick={onRemove}
          className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition"
        >
          Remove
        </button>
      </div>
    </div>
  )
}
```

---

### 3. **SizeChart** — Fit Information & Sizing

```typescript
interface SizeChartProps {
  selectedGarments: Garment[]
  userMeasurements?: {
    chest: number
    waist: number
    hips: number
  }
}

export const SizeChart: React.FC<SizeChartProps> = ({
  selectedGarments,
  userMeasurements,
}) => {
  const [expandedGarmentId, setExpandedGarmentId] = useState<string | null>(null)

  return (
    <div className="flex flex-col gap-4 p-4 border-t">
      <h2 className="text-lg font-semibold">Size & Fit</h2>

      {selectedGarments.length === 0 ? (
        <p className="text-center text-gray-500 text-sm">
          Select a garment to view sizing
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {selectedGarments.map((garment) => (
            <SizeChartItem
              key={garment.id}
              garment={garment}
              userMeasurements={userMeasurements}
              isExpanded={expandedGarmentId === garment.id}
              onToggle={() =>
                setExpandedGarmentId(
                  expandedGarmentId === garment.id ? null : garment.id
                )
              }
            />
          ))}
        </div>
      )}
    </div>
  )
}

interface SizeChartItemProps {
  garment: Garment
  userMeasurements?: { chest: number; waist: number; hips: number }
  isExpanded: boolean
  onToggle: () => void
}

const SizeChartItem: React.FC<SizeChartItemProps> = ({
  garment,
  userMeasurements,
  isExpanded,
  onToggle,
}) => {
  return (
    <div className="border rounded-lg overflow-hidden">
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-3 bg-gray-100 hover:bg-gray-200 transition"
      >
        <div className="text-left">
          <h4 className="font-semibold text-sm">{garment.name}</h4>
          <p className="text-xs text-gray-600">Available: {garment.sizes.join(', ')}</p>
        </div>
        <span className="text-lg">{isExpanded ? '▲' : '▼'}</span>
      </button>

      {/* Details */}
      {isExpanded && (
        <div className="p-3 bg-white flex flex-col gap-3">
          {/* Size Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-xs border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 font-semibold">Size</th>
                  <th className="text-center py-2 font-semibold">Bust</th>
                  <th className="text-center py-2 font-semibold">Length</th>
                  <th className="text-center py-2 font-semibold">Fit</th>
                </tr>
              </thead>
              <tbody>
                {garment.sizes.map((size) => {
                  const fit = garment.fitData?.[`size${size[0].toUpperCase()}`]
                  return (
                    <tr key={size} className="border-b">
                      <td className="py-2 font-semibold">{size}</td>
                      <td className="text-center">{fit?.bust || '—'} cm</td>
                      <td className="text-center">{fit?.length || '—'} cm</td>
                      <td className="text-center">{fit?.fit || 'Regular'}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {/* User Fit Assessment */}
          {userMeasurements && (
            <div className="bg-blue-50 p-3 rounded text-xs">
              <p className="font-semibold mb-2">Your Fit:</p>
              <p className="text-gray-700">
                Based on your measurements (chest: {userMeasurements.chest} cm),
                size <strong>M</strong> is recommended.
              </p>
            </div>
          )}

          {/* Buy Link */}
          <a
            href={garment.retailUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full py-2 bg-green-600 text-white rounded font-semibold hover:bg-green-700 transition text-center"
          >
            Buy Now
          </a>
        </div>
      )}
    </div>
  )
}
```

---

### 4. **SaveOutfitModal** — Save / Name Outfit

```typescript
interface SaveOutfitModalProps {
  outfitName: string
  onNameChange: (name: string) => void
  onSave: () => void
  onCancel: () => void
}

export const SaveOutfitModal: React.FC<SaveOutfitModalProps> = ({
  outfitName,
  onNameChange,
  onSave,
  onCancel,
}) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-sm">
        <h3 className="text-lg font-semibold mb-4">Save Outfit</h3>

        <input
          type="text"
          value={outfitName}
          onChange={(e) => onNameChange(e.target.value)}
          placeholder="Enter outfit name..."
          className="w-full px-3 py-2 border rounded-md mb-4 focus:outline-none focus:ring-2 focus:ring-black"
          autoFocus
        />

        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 py-2 bg-gray-200 text-gray-800 rounded font-semibold hover:bg-gray-300 transition"
          >
            Cancel
          </button>
          <button
            onClick={onSave}
            className="flex-1 py-2 bg-black text-white rounded font-semibold hover:bg-gray-800 transition"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}
```

---

## State Management

### Outfit Context

```typescript
interface OutfitContextType {
  selectedGarments: Garment[]
  outfitName: string
  isSaved: boolean
  addGarment: (garment: Garment) => void
  removeGarment: (garmentId: string) => void
  swapGarment: (garmentId: string, newGarment: Garment) => void
  setOutfitName: (name: string) => void
  saveOutfit: () => Promise<void>
  loadOutfit: (outfitId: string) => Promise<void>
  clearOutfit: () => void
}

export const OutfitContext = createContext<OutfitContextType | null>(null)

export const OutfitProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [selectedGarments, setSelectedGarments] = useState<Garment[]>([])
  const [outfitName, setOutfitName] = useState('Untitled Outfit')
  const [isSaved, setIsSaved] = useState(false)
  const { userId } = useAuth()
  const queryClient = useQueryClient()

  const addGarment = useCallback((garment: Garment) => {
    setSelectedGarments((prev) => {
      const exists = prev.some((g) => g.id === garment.id)
      return exists ? prev : [...prev, garment]
    })
    setIsSaved(false)
  }, [])

  const removeGarment = useCallback((garmentId: string) => {
    setSelectedGarments((prev) => prev.filter((g) => g.id !== garmentId))
    setIsSaved(false)
  }, [])

  const swapGarment = useCallback(
    (garmentId: string, newGarment: Garment) => {
      setSelectedGarments((prev) =>
        prev.map((g) => (g.id === garmentId ? newGarment : g))
      )
      setIsSaved(false)
    },
    []
  )

  const saveOutfit = useCallback(async () => {
    const response = await axios.post(`/api/users/${userId}/outfits`, {
      name: outfitName,
      garmentIds: selectedGarments.map((g) => g.id),
    })
    setIsSaved(true)
    queryClient.invalidateQueries(['outfits'])
  }, [outfitName, selectedGarments, userId, queryClient])

  const loadOutfit = useCallback(
    async (outfitId: string) => {
      const response = await axios.get(
        `/api/users/${userId}/outfits/${outfitId}`
      )
      const { name, garmentIds } = response.data
      setOutfitName(name)
      // Load garment details...
      setIsSaved(true)
    },
    [userId]
  )

  const clearOutfit = useCallback(() => {
    setSelectedGarments([])
    setOutfitName('Untitled Outfit')
    setIsSaved(false)
  }, [])

  return (
    <OutfitContext.Provider
      value={{
        selectedGarments,
        outfitName,
        isSaved,
        addGarment,
        removeGarment,
        swapGarment,
        setOutfitName,
        saveOutfit,
        loadOutfit,
        clearOutfit,
      }}
    >
      {children}
    </OutfitContext.Provider>
  )
}

export const useOutfit = () => {
  const context = useContext(OutfitContext)
  if (!context) {
    throw new Error('useOutfit must be used within OutfitProvider')
  }
  return context
}
```

---

## Data Flow Diagram

```
User Action                React State              API Call
─────────────────────────────────────────────────────────────

[Search/Filter] ─→ setSelectedCategory ─→ filter garments
                   setSearchQuery

[Click Garment] ─→ onGarmentAdd ─→ addGarment(outfitContext) 
                                      ↓
                   [3D Viewer updates]
                      (via Viewport3D props)

[Click Remove]  ─→ onGarmentRemove ─→ removeGarment ─→
                                        [3D Viewer updates]

[Save Outfit]   ─→ onSaveOutfit ─→ POST /api/outfits ─→
                                     [Success Toast]
                                     [isSaved = true]
```

---

## Styling & Responsiveness

### Responsive Breakpoints

```css
/* Mobile: 640px and up */
@media (min-width: 640px) {
  .sidebar {
    width: 360px;
  }
}

/* Tablet: 1024px and up */
@media (min-width: 1024px) {
  .garment-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### Fashion Aesthetic

- **Color Palette:** Neutral blacks, whites, grays with accent colors (e.g., product highlights)
- **Typography:** Clean, modern sans-serif (e.g., Inter, -apple-system)
- **Spacing:** Consistent grid-based spacing (4px, 8px, 16px, etc.)
- **Interactions:** Smooth transitions, hover states for all buttons

---

## Future Enhancements

1. **Wishlist / Favorites** — Star garments for later
2. **Outfit History** — View past outfit combinations
3. **Social Sharing** — Share outfits with friends (URL snapshots)
4. **Recommendation Engine** — Suggest complementary garments
5. **Outfit Comparison** — Side-by-side view of multiple outfits
6. **Custom Tags** — Tag outfits (e.g., "Casual", "Evening")

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-17
