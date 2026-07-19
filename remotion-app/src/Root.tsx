import "./index.css";
import { Composition } from "remotion";
import { EventReel } from "./EventReel";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="EventReel"
        component={EventReel}
        durationInFrames={510} // 17 seconds @ 30 FPS
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
