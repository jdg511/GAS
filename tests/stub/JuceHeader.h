// Minimal JUCE stand-in so the DSP headers can be compiled and checked without
// building JUCE. Only the handful of helpers ClipperCircuitModels.h touches.
#pragma once
#include <cmath>
#include <algorithm>

namespace juce
{
    template <typename T> inline T jmax (T a, T b) { return std::max (a, b); }
    template <typename T> inline T jmin (T a, T b) { return std::min (a, b); }
    template <typename T> inline T jlimit (T lo, T hi, T v) { return std::min (std::max (v, lo), hi); }
    template <typename T> inline T jmap (T v, T s0, T s1, T d0, T d1)
    {
        return d0 + (d1 - d0) * ((v - s0) / (s1 - s0));
    }

    struct Decibels
    {
        static float decibelsToGain (float db, float minusInfinityDb = -100.0f)
        {
            return db > minusInfinityDb ? std::pow (10.0f, db * 0.05f) : 0.0f;
        }
        static float gainToDecibels (float g, float floorDb = -100.0f)
        {
            return g > 0.0f ? std::max (floorDb, std::log10 (g) * 20.0f) : floorDb;
        }
    };

    template <typename T> struct MathConstants
    {
        static constexpr T twoPi = static_cast<T> (6.283185307179586476925286766559);
    };
}
