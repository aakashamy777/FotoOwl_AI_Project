# Remotion: Image with Ken Burns / Zoom

```tsx
import {Img, useCurrentFrame, interpolate} from 'remotion';

const scale = interpolate(useCurrentFrame(), [0, 90], [1, 1.1]);
<Img src={imageSrc} style={{transform: `scale(${scale})`, width: '100%', height: '100%', objectFit: 'cover'}} />
```

Use `interpolate` to animate scale/position over the sequence's frame range for slow zoom effects.
