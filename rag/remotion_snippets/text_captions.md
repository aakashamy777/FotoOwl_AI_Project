# Remotion: Caption Text with Fade

```tsx
import {useCurrentFrame, interpolate} from 'remotion';

const frame = useCurrentFrame();
const opacity = interpolate(frame, [0, 15, 75, 90], [0, 1, 1, 0]);
<div style={{opacity, fontSize: 48, fontFamily: 'sans-serif', textAlign: 'center'}}>
  {captionText}
</div>
```
