# Video package helper

`scripts/package.py` uses Python's standard library. `check` additionally requires `ffprobe` from FFmpeg on `PATH`. It creates no renders, writes no captions, and never publishes or schedules content.

Resolve `video_skill_dir` to the directory containing the loaded `SKILL.md`, using its actual absolute path from the skill catalog. This works for a repository copy or a shared installation, regardless of the current working directory.

```sh
video_skill_dir="/absolute/path/to/video-production"
python3 "$video_skill_dir/scripts/package.py" init /absolute/output-folder \
  --topic "Editing a video with AI and Remotion" --mode both-same \
  --source /absolute/source.mp4 \
  --platforms youtube,youtube-shorts,instagram,tiktok,linkedin
python3 "$video_skill_dir/scripts/package.py" check /absolute/output-folder/production.json
```

Repeat `--source` for additional input files. `init` validates arguments and source existence before creating the folder and refuses to overwrite an existing `production.json`. It creates only the manifest. The agent supplies the referenced files and edits metadata.

Modes are `horizontal` (landscape only), `vertical` (portrait only), `both-same` (both layouts using the same cut), or `both-distinct` (separate edits). Duration and orientation are independent: portrait need not mean a shorter cut. Both modes default YouTube and LinkedIn to landscape and other platforms to portrait. Change each platform's mapping if the brief calls for a different rendered variant. Defaults are YouTube, Instagram, TikTok, and LinkedIn. Supported optional targets are `youtube-shorts`, `threads`, `bluesky`, and `x`.

The schema has these fields:

```json
{
  "schema_version": 1,
  "topic": "The actual video topic",
  "mode": "horizontal",
  "state": "pending",
  "sources": ["/absolute/source.mp4"],
  "required_outputs": {
    "videos": ["landscape"],
    "captions": ["landscape"],
    "thumbnails": ["landscape"],
    "platform_metadata": ["youtube"]
  },
  "videos": {"landscape": {"path": "videos/landscape.mp4"}},
  "captions": {"landscape": {"path": "captions/landscape.srt", "reviewed": false}},
  "thumbnails": {"landscape": {"path": "thumbnails/landscape.png"}},
  "platforms": {
    "youtube": {
      "video": "landscape",
      "thumbnail": "landscape",
      "title": "A finished title",
      "description": "A finished description",
      "copy_path": "copy/youtube.md"
    }
  }
}
```

All output paths resolve relative to the manifest directory unless absolute. Source references must be absolute existing files. `title` is an editorial hook for platforms without a separate title field; `description` is the actual post caption there. Both remain required for every target. The copy file must contain the finished, paste-ready text. Check it against the JSON during editorial review; the helper only checks that this file exists and is nonempty UTF-8 text.

`captions.<variant>` associates a timed sidecar with `videos.<variant>`. Supply a UTF-8 `.srt` or `.vtt` and set `reviewed` to the JSON boolean `true` after reviewing its text and timing against the final edit. `init` creates separate paths with `reviewed: false`. For `both-same`, both mappings may use the same sidecar when their timing is identical:

```json
"captions": {
  "landscape": {"path": "captions/final.srt", "reviewed": true},
  "portrait": {"path": "captions/final.srt", "reviewed": true}
}
```

True closed captions are a sidecar or selectable embedded track. This helper requires an uploadable sidecar even when a video also embeds a selectable track. Burned-in social captions and platform post text do not satisfy this requirement. Keep clean masters, normally make additional burned-in social exports, and record those extra export paths with the edit instructions. Caption generation, accuracy, audio preservation and visual readability remain the agent's responsibility.

`init` leaves `state: pending`. `check` never changes state or the caption review flag. After technical and human-facing editorial/visual/audio/caption review, the agent can set `state: ready`. Reset `reviewed` to false when the associated edit's speech or timing changes. Publishing status should be recorded separately after a verified scheduler or platform response.

Only an explicit user exception can waive thumbnails or captions. Quote the exact instruction in the optional `waivers.thumbnails` or `waivers.captions` string and set the matching `required_outputs` list to `[]`. For thumbnails, also set every `platforms.<target>.thumbnail` to `null`. For example, `"waivers": {"thumbnails": "Just horizontal for YouTube, and this time skip thumbnails"}` records that user exception. For `"waivers": {"captions": "Skip all video captions for this delivery."}`, set `required_outputs.captions` to `[]`; no platform caption field is needed. `check` skips the waived asset type and explicitly reports the quoted instruction in its successful output. Empty or placeholder waivers fail. Videos and platform metadata cannot be waived. Never invent a waiver to bypass a missing, unavailable, or unfinished asset, including a missing transcription tool. `init` never creates waivers by default. A request for clean picture or no burned-in captions alone does not waive timed sidecars.

`check` returns nonzero with actionable errors for incomplete metadata, missing files, invalid variants or target names, and explicit `TODO`/`example.invalid` placeholders in required fields. It requires a thumbnail for each requested layout, including a landscape-only package without imposing a portrait thumbnail. It probes real media dimensions using `ffprobe`, accepting a 1.5% relative aspect-ratio tolerance around 16:9 or 9:16. Videos need a readable positive duration and frame rate. For `both-same`, durations must match within one frame at the slower of the two reported frame rates. This verifies duration agreement only; the agent must still verify identical content and timing. `both-distinct` permits different durations.

For every required caption mapping, `check` parses nonempty SRT or WebVTT cues. SRT uses increasing positive sequence numbers and `HH:MM:SS,mmm` timestamps. WebVTT uses its `WEBVTT` header and `MM:SS.mmm` or `HH:MM:SS.mmm` timestamps, with optional cue identifiers/settings and NOTE/STYLE/REGION blocks. Cue text must be nonblank after removing markup. A cue containing only `TODO` or beginning with `TODO:` fails as a placeholder; legitimate speech such as “This TODO comment needs a test.” is allowed. Start times must be ordered, end must be later than start, and no cue may extend beyond its associated video duration, allowing 1 ms rounding. Overlapping cues are permitted. A shared file is checked against both videos. `reviewed: true` records the agent's review; the helper cannot verify that attestation or detect every timing/content mismatch.

Passing these checks establishes file presence, caption structure and bounds, metadata completeness, aspect ratios, and duration consistency. It does not establish transcription accuracy, visual quality, speech cleanup, sync, platform eligibility, likeness accuracy, truthfulness, or permission to publish.
