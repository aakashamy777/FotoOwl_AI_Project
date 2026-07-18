# Remotion: Sequence

`Sequence` controls when a child renders, in frames.

```tsx
import {Sequence} from 'remotion';

<Sequence from={30} durationInFrames={90}>
  <MyScene />
</Sequence>
```

`from`: start frame. `durationInFrames`: how long it stays mounted.
Use for arranging scenes sequentially: from = cumulative sum of prior durations.
