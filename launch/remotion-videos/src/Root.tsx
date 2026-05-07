import React from 'react';
import { Composition } from 'remotion';
import { LaunchCountdown, TOTAL_FRAMES } from './videos/LaunchCountdown';
import { LaunchHero }  from './videos/LaunchHero';
import { StatReveal }  from './videos/StatReveal';
import { FeatureReel } from './videos/FeatureReel';
import { BeforeAfter } from './videos/BeforeAfter';
import { GradeTracker } from './videos/GradeTracker';
import {
  UGCGradeTracker,   UGCGradeTrackerFrames,
  UGCTransformation, UGCTransformationFrames,
  UGCPeerRec,        UGCPeerRecFrames,
} from './videos/UGCAds';

const W = 1080, H = 1920, FPS = 24;

export const Root: React.FC = () => (
  <>
    <Composition id="LaunchCountdown"   component={LaunchCountdown}   durationInFrames={TOTAL_FRAMES}           fps={FPS} width={W} height={H} />
    <Composition id="LaunchHero"        component={LaunchHero}        durationInFrames={720}                    fps={FPS} width={W} height={H} />
    <Composition id="StatReveal"        component={StatReveal}        durationInFrames={432}                    fps={FPS} width={W} height={H} />
    <Composition id="FeatureReel"       component={FeatureReel}       durationInFrames={720}                    fps={FPS} width={W} height={H} />
    <Composition id="BeforeAfter"       component={BeforeAfter}       durationInFrames={504}                    fps={FPS} width={W} height={H} />
    <Composition id="GradeTracker"      component={GradeTracker}      durationInFrames={432}                    fps={FPS} width={W} height={H} />
    <Composition id="UGCGradeTracker"   component={UGCGradeTracker}   durationInFrames={UGCGradeTrackerFrames}   fps={FPS} width={W} height={H} />
    <Composition id="UGCTransformation" component={UGCTransformation} durationInFrames={UGCTransformationFrames} fps={FPS} width={W} height={H} />
    <Composition id="UGCPeerRec"        component={UGCPeerRec}        durationInFrames={UGCPeerRecFrames}        fps={FPS} width={W} height={H} />
  </>
);
