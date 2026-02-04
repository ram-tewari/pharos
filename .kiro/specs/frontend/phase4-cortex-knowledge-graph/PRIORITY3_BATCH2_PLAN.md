# Priority 3 Batch 2: Responsive Design - Implementation Plan

**Status**: Ready to Start  
**Estimated Time**: 2-3 hours

## Goal

Make the Cortex Knowledge Graph feature work beautifully on all screen sizes (mobile, tablet, desktop) with touch-friendly interactions.

## Tasks

### 1. Add Responsive Breakpoints to GraphPage
**File**: `GraphPage.tsx`

**Changes**:
- Add responsive layout classes
- Stack panels vertically on mobile
- Hide/show panels with toggle buttons on mobile
- Adjust toolbar layout for mobile

**Breakpoints**:
- Mobile: `< 768px` (sm)
- Tablet: `768px - 1023px` (md)
- Desktop: `>= 1024px` (lg)

### 2. Make GraphToolbar Responsive
**File**: `GraphToolbar.tsx`

**Changes**:
- Wrap toolbar items on mobile
- Reduce button sizes on mobile
- Hide labels, show icons only on mobile
- Make search bar full-width on mobile

### 3. Make Side Panels Responsive
**Files**: `FilterPanel.tsx`, `NodeDetailsPanel.tsx`, `HypothesisPanel.tsx`

**Changes**:
- Full-width on mobile (slide over content)
- Slide-in animation from right
- Backdrop overlay on mobile
- Close on backdrop click

### 4. Add Touch Gestures to GraphCanvas
**File**: `GraphCanvas.tsx`

**Changes**:
- Pinch-to-zoom support
- Two-finger pan support
- Touch-friendly node sizes (minimum 44x44px)
- Prevent default touch behaviors

### 5. Make Buttons Touch-Friendly
**All Components**

**Changes**:
- Minimum 44x44px touch targets
- Adequate spacing between buttons (8px minimum)
- Larger tap areas on mobile

## Implementation Strategy

### Phase 1: Layout Responsiveness (1 hour)
1. Add responsive classes to GraphPage
2. Make toolbar responsive
3. Make panels slide-in on mobile

### Phase 2: Touch Interactions (1 hour)
1. Add touch gesture handlers
2. Increase touch target sizes
3. Test on mobile devices

### Phase 3: Polish & Testing (30 minutes)
1. Test on different screen sizes
2. Adjust spacing and sizing
3. Fix any layout issues

## Responsive Patterns

### Mobile-First Approach
```typescript
// Base styles for mobile
className="flex flex-col"

// Tablet and up
className="md:flex-row"

// Desktop and up
className="lg:gap-4"
```

### Panel Visibility
```typescript
// Mobile: Hidden by default, slide-in when opened
<aside className={`
  fixed inset-y-0 right-0 w-full
  transform transition-transform
  ${isOpen ? 'translate-x-0' : 'translate-x-full'}
  md:relative md:translate-x-0 md:w-80
`}>
```

### Touch Targets
```typescript
// Minimum 44x44px for touch
<Button className="min-h-[44px] min-w-[44px]">
```

### Responsive Toolbar
```typescript
// Mobile: Vertical or wrapped
<nav className="flex flex-wrap gap-2 md:flex-nowrap md:gap-4">
```

## Success Criteria

- [ ] Works on mobile (320px - 767px)
- [ ] Works on tablet (768px - 1023px)
- [ ] Works on desktop (1024px+)
- [ ] Touch targets >= 44x44px
- [ ] Panels slide-in on mobile
- [ ] Touch gestures work (pinch, pan)
- [ ] No horizontal scroll on mobile
- [ ] Content readable on all sizes

## Testing Checklist

- [ ] Test on iPhone (375px width)
- [ ] Test on Android (360px width)
- [ ] Test on iPad (768px width)
- [ ] Test on desktop (1024px+ width)
- [ ] Test pinch-to-zoom
- [ ] Test two-finger pan
- [ ] Test button tap areas
- [ ] Test panel slide-in/out

## Files to Modify

1. `GraphPage.tsx` - Main layout responsiveness
2. `GraphToolbar.tsx` - Toolbar responsiveness
3. `FilterPanel.tsx` - Panel slide-in on mobile
4. `NodeDetailsPanel.tsx` - Panel slide-in on mobile
5. `HypothesisPanel.tsx` - Panel slide-in on mobile
6. `GraphCanvas.tsx` - Touch gesture support

## Next Steps

1. Implement responsive layout
2. Add touch gestures
3. Test on multiple devices
4. Fix any issues
5. Document responsive behavior
