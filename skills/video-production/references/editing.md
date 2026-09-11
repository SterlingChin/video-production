# Editing and synchronization

## Dialogue

Keep a readable transcript and explicit retained source windows with reasons. The paper edit must retain the main point, why it matters, evidence, qualifications and ending. A polished sentence with the wrong causal story is a failed edit.

Local Whisper/Parakeet or a MacWhisper export can avoid uploading the recording for transcription. Discover installed tools and models first. In whisper.cpp, DTW timestamps may require `--no-flash-attn` (`-nfa`); check the installed CLI's help. `-nf` means no fallback and is different.

Long silence or accelerated sections can produce invented repeated speech and timestamp drift. Transcribe speech blocks separately and add source offsets. ASR can also collapse several attempts into one fluent line. Inspect short suspicious excerpts and the waveform instead of trusting one long transcript.

Word anchors sit inside words. Cut in surrounding quiet intervals, retaining initial consonants and trailing phonemes. Tiny audio edge fades prevent clicks. Quantize picture cuts consistently and concatenate contiguous audio before lossy encoding. Avoid many tiny cuts that destroy rhythm.

Normalize and inspect the result. Around -16 LUFS with headroom is a useful speech starting point, not a universal platform requirement. Keep transitions from jumping above speech. Preserve source resolution where useful and provide a practical sharing export.

## Screen Studio

Prefer an original `.screenstudio` project for a sharp independent camera panel. Enlarging a flattened camera bubble is a fallback. Do not overwrite the original project just to obtain another layout.

One observed package layout contains `recording/channel-1-display-0.mp4`, `channel-2-microphone-0.m4a`, `channel-3-webcam-0.mp4`, and `project.json` with `json.scenes[0].slices`. Inspect actual metadata: channel numbers, names, scenes, schema and offsets can differ.

For this slice schema:

```text
exportDuration = (sourceEndMs - sourceStartMs) / 1000 * timeScale
originalTime = sourceStartMs / 1000 + (exportTime - cumulativeExportStart) / timeScale
```

Intersect approved cuts with slice boundaries; a cut can cross a source jump. Preserve output frame counts when splitting. Account for actual track offsets and mirroring. Compare project duration with the reference export because saved state may differ from a prior export.

Verify synchronization against exported speech at several positions, including after speed changes. Speech-envelope correlation can separate small processing delay from a genuine mapping error. Measure corrections for this recording; never reuse another video's numeric offset. A differently edited screen-only export cannot be aligned by guessing a constant offset.

## Framing and QA

Frame input prompts, progress, result previews and closing separately when useful. Choose crops from representative frames rather than another recording's coordinates. Keep a synchronized webcam panel below the screen when it helps the vertical cut.

Preserve complete time-card text. Fit the whole card over a matching background if portrait cropping truncates it. Inspect first/last frames to exclude neighboring cards from a compilation.

For the same edit in multiple layouts, retain approved audio where possible, match frame totals and compare copied audio hashes. For separate long/short edits, keep independent source windows and transcripts.
