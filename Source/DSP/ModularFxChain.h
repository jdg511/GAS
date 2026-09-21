#pragma once

#include "FeedbackBlock.h"
#include "RevCStages.h"
#include "TankIRBlock.h"
#include "WetDryMixerBlock.h"

/** Rev C chain: input Vol (Tube) -> tanks -> Gain (Dirt) + Comp/Off/Limit -> feedback -> mix -> Output (Tube, Tape). */
struct ModularFxChain
{
    void prepare (double sampleRate, int maximumBlockSize)
    {
        inputStage.prepare (sampleRate, maximumBlockSize);
        leftTank.prepare (sampleRate, maximumBlockSize);
        leftTankSecondary.prepare (sampleRate, maximumBlockSize);
        rightTank.prepare (sampleRate, maximumBlockSize);
        rightTankSecondary.prepare (sampleRate, maximumBlockSize);
        dirtDynamics.prepare (sampleRate, maximumBlockSize);
        feedback.prepare (sampleRate, maximumBlockSize);
        wetDryMixer.prepare (sampleRate, maximumBlockSize);
        outputStage.prepare (sampleRate, maximumBlockSize);
    }

    void reset()
    {
        inputStage.reset();
        leftTank.reset();
        leftTankSecondary.reset();
        rightTank.reset();
        rightTankSecondary.reset();
        dirtDynamics.reset();
        feedback.reset();
        wetDryMixer.reset();
        outputStage.reset();
    }

    TubeTapeStage inputStage;      // Vol knob, pull for Tube (wet path only)
    TankIRBlock leftTank;
    TankIRBlock leftTankSecondary;
    TankIRBlock rightTank;
    TankIRBlock rightTankSecondary;
    DirtDynamicsBlock dirtDynamics; // Gain knob (pull for Dirt) + Comp / Off / Limit
    FeedbackBlock feedback;
    WetDryMixerBlock wetDryMixer;
    TubeTapeStage outputStage;     // Output knob, pull for Tape (tube too when Vol is pulled)
};
