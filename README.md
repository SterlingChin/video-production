# Video Production

Turn a recording into an edited video, matching thumbnails, and titles and descriptions for every destination. Give your agent the footage and the format; it carries the job through the finished package.

Built by [Sterling Chin](https://github.com/SterlingChin) from a real video-editing workflow with local transcription, Remotion, FFmpeg, and Screen Studio source tracks.

## Install

Use the official [Skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add SterlingChin/video-production --skill video-production
```

Choose your agent and installation scope in the prompts. To install globally for Codex and Claude Code:

```sh
npx skills add SterlingChin/video-production --skill video-production --agent codex claude-code --global
```

You can inspect what the repository contains before installing:

```sh
npx skills add SterlingChin/video-production --list
```

## Use it

In Codex:

> Use $video-production on this recording. Same edit in horizontal and vertical, for all socials.

In Claude Code:

> Use the video-production skill on this recording. Clean up the restarts and make a horizontal version for YouTube plus a separate vertical short.

The agent uses format choices already established in the conversation. If the choice is missing, it asks once and can begin inventory and transcription while you answer.

| Format | Result |
| --- | --- |
| Horizontal | A 16:9 edit at the requested length. |
| Vertical | A 9:16 edit at the requested length. |
| Same edit in both | The same story, cuts, audio and runtime, composed for each screen. |
| Separate long and short | A fuller horizontal edit and a vertical short that makes sense independently. |

Vertical does not automatically mean shorter. Your requested runtime and story govern the edit.

## What you get

- Speech cleanup that preserves the speaker's meaning, evidence and qualifications.
- The selected video versions, with inserts and time cards as the brief calls for them.
- Reviewed timed SRT or WebVTT captions for each layout, matched to the final edit. Identical edits can share a sidecar.
- Normally an additional social export with readable burned-in captions, alongside the clean master and selectable caption sidecar.
- A thumbnail or cover for every selected aspect ratio.
- Titles and independently copyable descriptions or captions for every selected platform.
- A production manifest and a technical completion check.

Default destinations are YouTube, Instagram, TikTok and LinkedIn. “All socials” adds Threads, Bluesky and X, plus YouTube Shorts when the edit includes vertical. Platforms without a separate title field receive an editorial hook or cover label alongside the caption. Your actual destination choices take precedence.

For screen walkthroughs, the workflow can use original Screen Studio screen and webcam tracks to put a sharp talking head beneath the demonstration. It checks the source timeline and synchronization instead of reusing another recording's crop or offset.

## Requirements and scope

This is an [Agent Skill](https://agentskills.io/specification): instructions and a package helper used by your agent. The helper initializes and verifies deliverables; the agent performs the editing and creative work.

- An agent with local file access, shell execution, and media review capabilities.
- Python 3.9 or newer and FFmpeg, including `ffprobe`, for the package helper.
- A transcription tool or an existing timed transcript. Local Whisper, Parakeet or MacWhisper can be used when available.
- Image creation or editing tools for thumbnails.
- Optional Remotion for programmatic video composition; optional Screen Studio source projects for separate screen and camera tracks.

Installation does not install these applications or grant access to an MCP server configured in another client. The agent discovers available tools and reports a concrete blocker when a required capability is missing. It does not silently omit a deliverable.

The workflow runs when you give it a production job. Publishing and scheduling happen only when you request them. Originals stay unchanged, and the creator's voice and branding come from the current brief.

## Package checker

From a clone of this repository:

```sh
python3 skills/video-production/scripts/package.py init /absolute/output-folder \
  --topic "A walkthrough of my project" \
  --mode both-same \
  --source /absolute/recording.mp4 \
  --platforms youtube,youtube-shorts,instagram,tiktok,linkedin

# After the agent supplies the media and fills in the manifest:
python3 skills/video-production/scripts/package.py check /absolute/output-folder/production.json
```

The checker verifies files, metadata, actual aspect ratios and matching runtime for the same edit in both layouts. Captions are required by default: each layout needs a reviewed SRT or WebVTT with nonempty, ordered cues inside its video duration. It rejects missing captions, invalid timing, empty text and TODO placeholders. Editorial, visual and audio review remain part of the agent's job.

True closed captions are sidecars or selectable embedded tracks. Burned-in text is an additional social export; post descriptions are separate copy. The package keeps an uploadable sidecar even when a selectable track is embedded. Caption revisions preserve the approved audio, and timing changes require another caption review. An explicit request to skip thumbnails or captions can be recorded as a visible exception; unavailable tools are not an exception.

See the [manifest reference](skills/video-production/references/package.md) for the schema.

## Development

The installable skill lives entirely in `skills/video-production/`, including its relative references, helper script, license and optional Codex UI metadata. Repository tests and contributor documentation stay outside the installed payload.

Run the integration and format checks with Python and FFmpeg installed:

```sh
python3 -m unittest discover -s tests -v
```

The [Agent Skills reference validator](https://github.com/agentskills/agentskills/tree/main/skills-ref) can additionally validate the format. That optional development tool requires Python 3.11 or newer:

```sh
skills-ref validate skills/video-production
```

To propose a change, describe the recording or request that exposed the problem, preserve the user's format and publication choices, and include a regression check when changing the helper's behavior. Use generated fixtures instead of private footage or transcripts.

## skills.sh

Find the skill on [skills.sh](https://skills.sh/sterlingchin/video-production/video-production).

This repository follows the public GitHub distribution path documented by [skills.sh](https://skills.sh/docs/faq). The directory discovers skills through installs made with the Skills CLI's telemetry enabled. Indexing is managed by skills.sh; a successful installation does not guarantee immediate directory visibility.

## License

[MIT](LICENSE). No recordings, third-party media, model weights, or API credentials are included.
