import "./index.css";
import { Composition } from "remotion";
import { EventReel } from "./EventReel";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="EventReel"
        component={EventReel}
        durationInFrames={390} // 13 seconds @ 30 FPS (5 scenes * 90 - 4 transitions * 15)
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
