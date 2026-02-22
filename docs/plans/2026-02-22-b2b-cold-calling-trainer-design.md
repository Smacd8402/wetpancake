# B2B Cold Calling Trainer Design

**Date:** 2026-02-22
**Status:** Approved

## 1. Product Goal
Build a local, real-time voice training assistant for B2B cold calling reps that can run on a single Windows PC with no paid APIs. The system should support high-repetition practice with non-repetitive conversations and measurable performance improvement over time.

## 2. Constraints and Requirements
- Must run locally on a Windows PC with:
  - AMD Radeon RX 6700 XT
  - AMD Ryzen 7 5800X3D (8-core)
  - 32 GB DDR4 RAM
- No paid API services.
- Real-time voice conversation is required.
- Session variety must support 100+ uses without obvious repetition.
- First version call length target: 5-8 minutes.
- Training style: single live prospect persona per call, with post-call scoring.

## 3. Architecture
### 3.1 Process Model
- Electron desktop app provides UI, session controls, and local app lifecycle.
- Local Python runtime provides AI services:
  - STT (speech-to-text)
  - Dialogue engine (prospect behavior)
  - TTS (text-to-speech)
- SQLite database stores sessions, scorecards, persona metadata, and anti-repeat signals.

### 3.2 Real-Time Call Loop
1. Capture user microphone audio in short chunks.
2. Run incremental STT transcription.
3. Detect end-of-turn with silence and intent heuristics.
4. Generate prospect response from local LLM and conversation state.
5. Stream response audio via TTS back to trainee.
6. Persist each turn to SQLite for analytics and replay.

## 4. Conversation Diversity Design
### 4.1 Session Generation
Each session creates a fresh prospect profile with:
- Industry and sub-vertical
- Role and seniority
- Personality and communication style
- Core pain points
- Buying urgency
- Primary and secondary objection tendencies

### 4.2 Anti-Repeat Strategy
- Store a unique generation seed per session and block recent seed reuse.
- Track opening turn patterns and prevent near-duplicates in rolling windows.
- Track primary objection types and close outcomes to avoid repeated arcs.
- Use semantic similarity thresholds against recent sessions to reject near-duplicate conversations before call start.

### 4.3 Behavioral Adaptation
The prospect is stateful and reactive rather than script-only:
- Interruptions and weak discovery change trust and resistance.
- Strong positioning can reduce objection intensity.
- Conversation can branch toward hang-up, continue, or next-step agreement.

## 5. Training and Scoring
### 5.1 Session Flow
- Start with realistic cold open.
- Run uninterrupted conversation (no in-call coaching for V1).
- End on natural close, disqualification, hang-up, or time cap.
- Produce immediate post-call review.

### 5.2 Score Dimensions
Weighted scorecard:
- Opener clarity
- Rapport and tone
- Discovery depth
- Objection handling
- Value articulation
- Close attempt quality
- Talk/listen balance

### 5.3 Feedback Outputs
After each run:
- Overall score and per-dimension scores
- Top 3 misses with better phrasing suggestions
- One transcript replay comparison (actual vs stronger alternative)
- Trend view across sessions to show improvement over repetition

## 6. Reliability and Deployment
### 6.1 Runtime Resilience
- Audio watchdog auto-recovers from temporary mic drop.
- Health checks for STT/TTS/LLM services with restart behavior.
- Fallback to text response if TTS fails so practice continues.
- Autosave conversation state each turn.

### 6.2 Local Installation
- Single desktop installer bundles Electron app and local Python runtime launcher.
- First-run checks model availability and hardware fit.
- Offline-first after model installation.

## 7. Performance Targets (Current Hardware)
- Target response latency per turn: ~1.2s to 2.5s average after trainee turn ends.
- Stable 5-8 minute sessions without remote services.

## 8. Future Hardware Upgrade Path
- Keep model execution behind a provider abstraction so larger local models can be swapped in later.
- Preserve UI, scoring, database, and reporting layers while upgrading inference backends.

## 9. V1 Stack Decision
Selected V1 stack:
- App shell: Electron desktop
- STT: lighter local option for speed on current hardware
- TTS: lighter local option for low latency
- Dialogue model: local LLM runtime (no paid APIs)
- Persistence: SQLite

This design is approved and ready for implementation planning.
