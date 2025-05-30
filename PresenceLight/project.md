Project Name: Presence Light

Concept:
A minimal daemon (or service) that observes your computer activity—terminal focus, open windows, typing cadence, or even browser tab switches—and uses simple heuristics to infer whether you're present, distracted, or idle. It then uses this to control a small visible artifact:

A softly glowing desktop tray icon,

Or an ambient RGB light (via USB or networked LED strip),

Or a small local web interface with subtle animation.

This artifact becomes a passive, ambient signal—like a mood ring but for cognitive presence.

Modes (based on heuristics):
* Focused: steady glow or a calm waveform
* Fragmented: flickers gently, color shifts to indicate tab switches or context flips
* Absent: fades to near-dark or cold blue

Optional: integrate with calendar to know when you're supposed to be focused, or check audio activity to detect meetings.

Some thoughts:
Not productivity porn: It's about awareness, not gamification.
Small, complete, evocative: You could write a prototype in an afternoon and tune the vibe forever.
Expandable: You can plug it into Home Assistant later, or make the signals poetic (e.g., show a quote when you're absent).
Meta: You’re coding a thing that watches you code and subtly asks, "Are you here?"
