# Remotion: TransitionSeries (crossfade / wipe / slide)

```tsx
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={90}>
    <Scene1 />
  </TransitionSeries.Sequence>
  <TransitionSeries.Transition
    presentation={fade()}
    timing={linearTiming({durationInFrames: 15})}
  />
  <TransitionSeries.Sequence durationInFrames={90}>
    <Scene2 />
  </TransitionSeries.Sequence>
</TransitionSeries>
```

Requires `@remotion/transitions` package. Use `fade()` for cinematic/corporate, `slide()` for upbeat.
