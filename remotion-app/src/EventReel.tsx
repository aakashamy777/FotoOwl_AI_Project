import {Img, useCurrentFrame, interpolate} from 'remotion';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import React from 'react';

// Each scene runs for 3 seconds @ 30 FPS = 90 frames.
// Transitions run for 0.5 seconds @ 30 FPS = 15 frames.

const Scene = ({ imageSrc, caption }: { imageSrc: string; caption: string }) => {
  const frame = useCurrentFrame();
  
  // Ken Burns zoom effect: scale from 1 to 1.1 over 90 frames
  const scale = interpolate(frame, [0, 90], [1, 1.1], {
    extrapolateRight: 'clamp',
  });
  
  // Caption opacity fade: fade in over first 15 frames, hold, fade out over last 15 frames
  const captionOpacity = interpolate(frame, [0, 15, 75, 90], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden' }}>
      <Img 
        src={imageSrc} 
        style={{
          transform: `scale(${scale})`,
          width: '100%',
          height: '100%',
          objectFit: 'cover'
        }} 
      />
      {caption && (
        <div style={{
          position: 'absolute',
          bottom: 100,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          opacity: captionOpacity,
        }}>
          <div style={{
            background: 'rgba(0, 0, 0, 0.6)',
            padding: '16px 32px',
            borderRadius: '8px',
            color: '#ffffff',
            fontSize: 48,
            fontFamily: 'Helvetica, Arial, sans-serif',
            fontWeight: 'bold',
            textAlign: 'center',
            maxWidth: '80%',
          }}>
            {caption}
          </div>
        </div>
      )}
    </div>
  );
};

export const EventReel = () => {
  return (
    <TransitionSeries>
      {/* Scene 1 */}
      <TransitionSeries.Sequence durationInFrames={90}>
        <Scene 
          imageSrc="data/input_images/AHD_6008.jpg" 
          caption="A beautiful beginning..." 
        />
      </TransitionSeries.Sequence>
      
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({durationInFrames: 15})}
      />
      
      {/* Scene 2 */}
      <TransitionSeries.Sequence durationInFrames={90}>
        <Scene 
          imageSrc="data/input_images/AHD_6106.jpg" 
          caption="Shared with loved ones." 
        />
      </TransitionSeries.Sequence>
      
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({durationInFrames: 15})}
      />
      
      {/* Scene 3 */}
      <TransitionSeries.Sequence durationInFrames={90}>
        <Scene 
          imageSrc="data/input_images/AHD_6142.jpg" 
          caption="Moments to cherish forever." 
        />
      </TransitionSeries.Sequence>
      
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({durationInFrames: 15})}
      />
      
      {/* Scene 4 */}
      <TransitionSeries.Sequence durationInFrames={90}>
        <Scene 
          imageSrc="data/input_images/AHD_6148.jpg" 
          caption="Laughter and joy." 
        />
      </TransitionSeries.Sequence>
      
      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({durationInFrames: 15})}
      />
      
      {/* Scene 5 */}
      <TransitionSeries.Sequence durationInFrames={90}>
        <Scene 
          imageSrc="data/input_images/DSC_4491.jpg" 
          caption="Together, always." 
        />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
