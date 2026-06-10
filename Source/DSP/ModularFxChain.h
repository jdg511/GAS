#pragma once

#include "FeedbackBlock.h"
#include "FilterClipperBlock.h"
#include "TankIRBlock.h"
#include "StereoTankCrossfadeBlock.h"
#include "WetDryMixerBlock.h"

struct ModularFxChain
{
    void prepare (double sampleRate, int maximumBlockSize)
    {
        leftTank.prepare (sampleRate, maximumBlockSize);
        leftTankSecondary.prepare (sampleRate, maximumBlockSize);
        rightTank.prepare (sampleRate, maximumBlockSize);
        rightTankSecondary.prepare (sampleRate, maximumBlockSize);
        stereoTankCrossfade.prepare (sampleRate, maximumBlockSize);
        filterClipper.prepare (sampleRate, maximumBlockSize);
        feedback.prepare (sampleRate, maximumBlockSize);
        wetDryMixer.prepare (sampleRate, maximumBlockSize);
    }

    void reset()
    {
        leftTank.reset();
        leftTankSecondary.reset();
        rightTank.reset();
        rightTankSecondary.reset();
        stereoTankCrossfade.reset();
        filterClipper.reset();
        feedback.reset();
        wetDryMixer.reset();
    }

    TankIRBlock leftTank;
    TankIRBlock leftTankSecondary;
    TankIRBlock rightTank;
    TankIRBlock rightTankSecondary;
    StereoTankCrossfadeBlock stereoTankCrossfade;
    FilterClipperBlock filterClipper;
    FeedbackBlock feedback;
    WetDryMixerBlock wetDryMixer;
};
