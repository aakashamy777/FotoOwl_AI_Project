# Remotion: Registering a Composition

```tsx
import {Composition} from 'remotion';

<Composition
  id="EventReel"
  component={EventReel}
  durationInFrames={450}
  fps={30}
  width={1080}
  height={1920}
/>
```

Register in `src/Root.tsx`. `durationInFrames` must match the sum of all sequence durations. fps=30 standard.
