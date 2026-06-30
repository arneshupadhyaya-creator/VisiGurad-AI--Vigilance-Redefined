import { useRef, useState } from 'react';
import { analyzeTyping } from '../services/aiClient';

/**
 * useTypingCapture Hook
 * Purpose: Captures keystroke timing dynamics invisibly without logging actual keys/passwords.
 * Responsibility: Track key down/up deltas, calculate flight/hold times, speeds, paste actions, and send statistics to backend.
 */
export const useTypingCapture = (onResultCallback) => {
  // Telemetry logs kept in refs to avoid re-renders during fast typing
  const timingsRef = useRef({
    keyTimes: {}, // keycode -> pressTime
    holdTimes: [],
    flightTimes: [],
    lastKeyReleaseTime: 0,
    lastKeypressTime: 0,
    backspaceCount: 0,
    totalKeys: 0,
    pasteDetected: false,
    autoFillDetected: false,
    startTime: 0,
    lastEventTime: 0,
    idleTimes: []
  });

  const [riskLevel, setRiskLevel] = useState('LOW');
  const [analyzing, setAnalyzing] = useState(false);

  const resetCapture = () => {
    timingsRef.current = {
      keyTimes: {},
      holdTimes: [],
      flightTimes: [],
      lastKeyReleaseTime: 0,
      lastKeypressTime: 0,
      backspaceCount: 0,
      totalKeys: 0,
      pasteDetected: false,
      autoFillDetected: false,
      startTime: 0,
      lastEventTime: 0,
      idleTimes: []
    };
    setRiskLevel('LOW');
  };

  const handleKeyDown = (e) => {
    const time = Date.now();
    const keyCode = e.keyCode;

    // Start timer on first keypress
    if (timingsRef.current.startTime === 0) {
      timingsRef.current.startTime = time;
    }

    timingsRef.current.totalKeys += 1;
    timingsRef.current.keyTimes[keyCode] = time;

    // Calculate flight time
    if (timingsRef.current.lastKeyReleaseTime !== 0) {
      const flight = time - timingsRef.current.lastKeyReleaseTime;
      timingsRef.current.flightTimes.push(flight);
    }

    // Calculate idle time (pause between typing sessions)
    if (timingsRef.current.lastEventTime !== 0) {
      const pause = time - timingsRef.current.lastEventTime;
      if (pause > 1500) {
        timingsRef.current.idleTimes.push(pause);
      }
    }

    if (e.key === 'Backspace') {
      timingsRef.current.backspaceCount += 1;
    }

    timingsRef.current.lastKeypressTime = time;
    timingsRef.current.lastEventTime = time;
  };

  const handleKeyUp = (e) => {
    const time = Date.now();
    const keyCode = e.keyCode;

    if (timingsRef.current.keyTimes[keyCode]) {
      const hold = time - timingsRef.current.keyTimes[keyCode];
      timingsRef.current.holdTimes.push(hold);
      delete timingsRef.current.keyTimes[keyCode];
    }

    timingsRef.current.lastKeyReleaseTime = time;
    timingsRef.current.lastEventTime = time;
  };

  const handlePaste = () => {
    timingsRef.current.pasteDetected = true;
  };

  const handleInput = (e) => {
    // If multiple characters are inserted instantly without keypress events, it is autofill
    if (e.target.value.length > 5 && timingsRef.current.totalKeys < 2) {
      timingsRef.current.autoFillDetected = true;
    }
  };

  const compileMetrics = () => {
    const ref = timingsRef.current;
    const holdTimes = ref.holdTimes;
    const flightTimes = ref.flightTimes;
    const totalTimeMs = ref.lastEventTime - ref.startTime || 1;

    // Statistical calculations
    const mean = (arr) => arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0;
    const holdMean = mean(holdTimes);
    const flightMean = mean(flightTimes);

    // Variance
    const variance = (arr, avg) => arr.length 
      ? arr.reduce((a, b) => a + Math.pow(b - avg, 2), 0) / arr.length 
      : 0;
    const holdVar = variance(holdTimes, holdMean);

    // Speed calculation
    const minutes = totalTimeMs / 60000;
    const wpm = minutes > 0 ? (ref.totalKeys / 5) / minutes : 0;
    const typingSpeed = minutes > 0 ? ref.totalKeys / minutes : 0;

    // Error rate
    const errorRate = ref.totalKeys > 0 ? ref.backspaceCount / ref.totalKeys : 0;

    // Consistency (inverse of hold variance)
    const consistency = holdVar > 0 ? Math.min(100, Math.round(10000 / holdVar)) : 100;

    return {
      holdTime: Math.round(holdMean),
      flightTime: Math.round(flightMean),
      digraphLatency: Math.round(holdMean + flightMean),
      trigraphLatency: Math.round(holdMean * 2 + flightMean),
      typingSpeed: Math.round(typingSpeed),
      wpm: Math.round(wpm),
      burstSpeed: Math.round(typingSpeed * 1.2),
      variance: Math.round(holdVar),
      consistency,
      backspaceFrequency: ref.backspaceCount,
      idleTime: Math.round(mean(ref.idleTimes)),
      errorRate: parseFloat(errorRate.toFixed(3)),
      pasteDetected: ref.pasteDetected,
      autoFillDetected: ref.autoFillDetected
    };
  };

  const submitTypingProfile = async () => {
    const metrics = compileMetrics();
    // Do not submit telemetry if the user didn't write anything substantial (skip single character taps)
    if (metrics.typingSpeed === 0 && !metrics.autoFillDetected && !metrics.pasteDetected) {
      return;
    }

    setAnalyzing(true);
    try {
      const response = await analyzeTyping(metrics);
      if (response.status === 'success') {
        const assessment = response.data;
        setRiskLevel(assessment.risk_level);
        if (onResultCallback) {
          onResultCallback(assessment);
        }
      }
    } catch (err) {
      console.error('Typing behavior profile submission error:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  return {
    riskLevel,
    analyzing,
    resetCapture,
    typingHandlers: {
      onKeyDown: handleKeyDown,
      onKeyUp: handleKeyUp,
      onPaste: handlePaste,
      onInput: handleInput
    },
    submitTypingProfile
  };
};
