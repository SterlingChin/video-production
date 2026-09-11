---
name: video-production
description: Turn recordings into finished video packages with speech cleanup, horizontal or vertical edits, timed captions, thumbnails, and platform titles and descriptions. Use for requests to edit footage, make social versions, or package an existing video for publication.
license: MIT
metadata:
  author: SterlingChin
  version: "1.0.1"
---

# Video Production

Requires an agent with local file and shell access, Python 3.9+, FFmpeg/ffprobe, and tools for transcription, media review, and image creation. Remotion and Screen Studio are optional.

Run the complete production job after the output formats are clear. A package includes the requested video versions, reviewed timed captions for each edit, matching thumbnails, and a title plus post description/caption for every selected platform. Do not wait for the user to request the packaging pieces separately. A social post caption is copy; it does not replace video subtitles.

This is an agent-run workflow invoked with footage or an existing edit. It does not install a watcher, start a recurring job, or publish by itself.

## Set the brief once

Use the current request and accepted decisions first. Distinguish aspect ratio from editorial length:

| Mode | Deliverables |
| --- | --- |
| `horizontal` | One 16:9 edit, with the depth the story needs. |
| `vertical` | One 9:16 edit, at the requested length and focus. |
| `both-same` | The same story, cuts, runtime and audio in 16:9 and 9:16. Recompose the picture. |
| `both-distinct` | A fuller 16:9 story and a separately edited 9:16 short that makes sense on its own. |

If this choice is missing, ask one concise question offering these options. Start inventory and transcription while the answer is pending. Do not infer a shorter story solely from a vertical aspect ratio or ask again when the user already chose.

Record the topic, intended takeaway, sources, chosen mode, desired lengths if stated, destinations, accepted style decisions, and supplied inserts/screenshots. Use the current user or project's voice, branding, and account preferences; do not assume the skill author is the presenter. Preserve meaning before optimizing runtime. For a revision, carry forward the approved brief and deliverables.

Usual destinations: YouTube, Instagram, TikTok and LinkedIn. **All socials** also includes Threads, Bluesky and X, plus YouTube Shorts when the chosen mode includes vertical. Include separate YouTube Shorts metadata for that version. Existing account choices take precedence. Channel selection for copy does not authorize posting.

Create a per-video output directory near the media or where requested. Keep working proxies/cache separately, source files unchanged, and reusable edit instructions alongside the work. Use [the package helper](references/package.md) to initialize and check the manifest. It organizes and verifies files; the agent performs the editing and creative work.

## Review and edit

1. Inventory footage and original editor projects. Probe duration, dimensions, frame rate and audio. Check available tools; a Remotion MCP configured in another client may not be accessible here.
2. Obtain a local transcript with timing, preferably from an existing transcript or installed model. Review representative frames and the complete spoken narrative. Read [editing and synchronization](references/editing.md) for cleanup or separate Screen Studio tracks.
3. Select the strongest complete takes. Remove stutters, repeated attempts, abandoned phrases and unnecessary waiting. Retain qualifications, causal links, evidence and the intended payoff. Preserve conversational rhythm and phonetic handles. Do not manufacture new spoken claims.
4. Replace accelerated waits with supplied time cards when requested or appropriate to this brief. Do not add the same joke to every future video. Keep quote screenshots and redactions intact; highlights must reflect the actual quote.
5. Build the requested variants. Use available Remotion tools for repeatable captions, graphics and animation; FFmpeg suits trims, reframing and audio work. An existing conventional edit can be the source. Choose tools that complete this job rather than requiring a particular editor.
6. For screen walkthroughs, prefer original separate screen and webcam tracks. A useful vertical layout is screen above, sharp talking head below, with full-frame intro/closing when appropriate. Crop or pan to useful UI and retain the result preview/captions. This is a layout choice, not a rule for all footage.
7. Create timed captions from the final edited speech, including any changed cuts, waits, cards and speed changes. Carry forward caption/overlay preferences. For `both-same`, preserve approved audio when only the picture changes. For `both-distinct`, create and review captions for each edit independently. See [caption review](references/editing.md#captions).

Continue through packaging and verification; a rough cut alone does not complete this workflow.

## Always package

Read [thumbnails and social copy](references/packaging.md).

These are the default package requirements. Honor an explicit exception in the current brief, such as skipping thumbnails or captions for one job. Record the exact instruction in the manifest's documented waiver, report the exception in delivery, and retain the other requirements. Never create a waiver to hide a missing asset or unavailable tool.

- Export a reviewed SRT or WebVTT sidecar for every selected video layout. The same story in both layouts may share a file when timing is identical. True closed captions are a selectable track or a sidecar used by the player; burned-in text alone is not closed captions. Keep an uploadable sidecar even when also embedding a selectable track.
- Normally also export a version with burned-in captions for social viewing. Keep a clean master and caption sidecar. Use readable, uncluttered framing and avoid faces, important UI and platform controls. Preserve approved audio when adding captions. An explicit preference for clean picture governs the burned-in export; it does not waive the timed sidecar.
- Produce a landscape thumbnail for the landscape version and a portrait cover for the portrait version. Keep them consistent for one release. Use a real, well-chosen frame of the presenter and an accurate, readable hook. Inspect identity, text and cropping. Save selected files with the video.
- Write a title and description/caption for every destination. For platforms without a separate title field, label the title an **editorial hook/cover label** and make the caption independently copyable. Supply appropriate metadata for distinct edits. Avoid duplicated hooks when a caption already begins with its hook.
- Ground copy in the final edit. Distinguish demonstrated results from future ideas. Do not invent public links, measured time savings or platform capabilities. Keep missing-link notes outside paste-ready copy.
- Save a combined copy document and clean per-platform files. Update the manifest with actual video, caption, cover and copy paths, titles and descriptions. Mark each caption mapping `reviewed: true` only after reviewing text and timing against its final video. Record additional social exports alongside the edit instructions.

## Verify and deliver

Check the story and actual exports: decode, duration/frame count, picture/audio alignment, cut and card edges, framing, and audio levels. Review the finished transcript when speech changed; suspicious short excerpts can expose retakes hidden by a longer ASR pass. Do not claim to have listened when only transcript or signal analysis was available.

For picture-only revisions, verify approved audio is unchanged. For `both-same`, confirm equal runtime and the same narrative; equal duration alone does not prove identical edits. For distinct cuts, check each ending and context independently.

Run the package helper's `check` command. Missing or unreviewed timed captions, covers, or platform titles/descriptions mean the package is unfinished unless explicitly waived as documented. Fix omissions or report the specific blocker without claiming completion. The helper validates caption structure and bounds; it does not establish transcription accuracy, judge narrative quality, or perform publication.

Show finished media, link the caption sidecars and copy package, and state runtime/format. Label clean masters, selectable captions and burned-in social exports accurately. Keep the manifest and edit instructions available. During revisions, update changed items and affected dependencies, including caption timing; reuse assets that still match.

Publish or schedule only when requested. Honor session authorization already given. Verify connected accounts, destination, date/timezone and current platform options. Record scheduler confirmation before claiming scheduled, avoid duplicate jobs, and never substitute a reminder for a scheduled post. Drafts are not shipped content.
