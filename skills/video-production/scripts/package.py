#!/usr/bin/env python3
"""Initialize or verify a video delivery package. Never render or publish media."""

import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

MODES = ("horizontal", "vertical", "both-same", "both-distinct")
PLATFORMS = ("youtube", "youtube-shorts", "instagram", "tiktok", "linkedin", "threads", "bluesky", "x")
DEFAULT_PLATFORMS = "youtube,instagram,tiktok,linkedin"
ASPECTS = {"landscape": 16 / 9, "portrait": 9 / 16}


def variants(mode):
    return ["landscape"] if mode == "horizontal" else ["portrait"] if mode == "vertical" else ["landscape", "portrait"]


def meaningful(value):
    return (isinstance(value, str) and bool(value.strip())
            and value.strip().upper() != "TODO"
            and not value.strip().upper().startswith("TODO:")
            and "example.invalid" not in value.lower())


def init_package(args):
    targets = [item.strip() for item in args.platforms.split(",")]
    if not targets or any(item not in PLATFORMS for item in targets):
        raise ValueError("--platforms must contain only: " + ", ".join(PLATFORMS))
    if len(set(targets)) != len(targets):
        raise ValueError("--platforms contains duplicates")
    if not meaningful(args.topic):
        raise ValueError("--topic must contain a real topic, not an empty value or TODO")
    sources = [str(Path(item).expanduser().resolve()) for item in args.source]
    for source in sources:
        if not Path(source).is_file():
            raise ValueError(f"Source file does not exist: {source}")
    root = Path(args.output_dir).expanduser().resolve()
    manifest_path = root / "production.json"
    if manifest_path.exists():
        raise ValueError(f"Refusing to overwrite {manifest_path}")
    if root.exists() and not root.is_dir():
        raise ValueError(f"Output directory is a file: {root}")
    needed = variants(args.mode)
    manifest = {
        "schema_version": 1, "topic": args.topic, "mode": args.mode, "state": "pending",
        "sources": sources,
        "required_outputs": {"videos": needed, "thumbnails": needed, "platform_metadata": targets},
        "videos": {key: {"path": f"videos/{key}.mp4"} for key in needed},
        "thumbnails": {key: {"path": f"thumbnails/{key}.png"} for key in needed},
        "platforms": {},
    }
    for target in targets:
        variant = needed[0] if len(needed) == 1 else "landscape" if target in ("youtube", "linkedin") else "portrait"
        manifest["platforms"][target] = {
            "video": variant, "thumbnail": variant, "title": "", "description": "",
            "copy_path": f"copy/{target}.md",
        }
    root.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"Created {manifest_path}; fill metadata and supply all referenced outputs before checking.")


def probe(path, ffprobe):
    result = subprocess.run(
        [ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,duration,avg_frame_rate:format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode:
        raise ValueError(result.stderr.strip() or "ffprobe could not read this file")
    data = json.loads(result.stdout)
    streams = data.get("streams", [])
    if not streams:
        raise ValueError("no readable image/video stream")
    stream = streams[0]
    width, height = int(stream.get("width", 0)), int(stream.get("height", 0))
    if min(width, height) <= 0:
        raise ValueError("missing dimensions")
    raw_duration = stream.get("duration", data.get("format", {}).get("duration", 0))
    duration = float(raw_duration) if raw_duration != "N/A" else float(data.get("format", {}).get("duration", 0))
    numerator, denominator = stream.get("avg_frame_rate", "0/1").split("/")
    fps = float(numerator) / float(denominator) if float(denominator) else 0
    return width, height, duration, fps


def check_package(args):
    manifest_path = Path(args.manifest).expanduser().resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Manifest must be a JSON object")
    errors = []
    root = manifest_path.parent
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        errors.append("ffprobe is required to verify real media dimensions and duration; install FFmpeg and rerun check")
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not meaningful(data.get("topic")):
        errors.append("topic must be nonblank and contain no TODO or example.invalid placeholder")
    mode = data.get("mode")
    if mode not in MODES:
        errors.append("mode must be one of: " + ", ".join(MODES))
    needed = variants(mode) if mode in MODES else []
    waivers = data.get("waivers", {})
    if not isinstance(waivers, dict):
        errors.append("waivers must be an object containing only an explicit thumbnails exception")
        waivers = {}
    for key in waivers:
        if key != "thumbnails":
            errors.append(f"waivers.{key}: only thumbnails can be waived")
    thumbnail_waiver = waivers.get("thumbnails")
    if "thumbnails" in waivers and not meaningful(thumbnail_waiver):
        errors.append("waivers.thumbnails: quote the exact explicit user instruction; blank or placeholder waivers are invalid")
    waived_thumbnails = meaningful(thumbnail_waiver)
    needed_thumbnails = [] if waived_thumbnails else needed

    def file_reference(value, label, absolute=False):
        if not meaningful(value):
            errors.append(f"{label}: provide a real file path")
            return None
        path = Path(value).expanduser()
        if absolute and not path.is_absolute():
            errors.append(f"{label}: source references must be absolute")
            return None
        path = path if path.is_absolute() else root / path
        if not path.is_file():
            errors.append(f"{label}: missing file {path}")
            return None
        return path

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a nonempty list of absolute source file paths")
    else:
        for index, source in enumerate(sources):
            file_reference(source, f"sources[{index}]", absolute=True)

    platforms = data.get("platforms")
    if not isinstance(platforms, dict) or not platforms:
        errors.append("platforms must contain at least one supported platform with title, description, and copy_path")
        platforms = {}
    requirements = data.get("required_outputs", {})
    if not isinstance(requirements, dict):
        requirements = {}
    for key, expected in (("videos", needed), ("thumbnails", needed_thumbnails), ("platform_metadata", list(platforms))):
        actual = requirements.get(key)
        if not isinstance(actual, list) or sorted(map(str, actual)) != sorted(expected):
            errors.append(f"required_outputs.{key} must be {expected}")

    video_info = {}
    for kind in ("videos", "thumbnails"):
        entries = data.get(kind, {})
        if not isinstance(entries, dict):
            entries = {}
        for variant in needed if kind == "videos" else needed_thumbnails:
            label = f"{kind}.{variant}"
            entry = entries.get(variant, {})
            path = file_reference(entry.get("path") if isinstance(entry, dict) else None, label + ".path")
            if not path or not ffprobe:
                continue
            try:
                width, height, duration, fps = probe(path, ffprobe)
                if abs((width / height) / ASPECTS[variant] - 1) > 0.015:
                    errors.append(f"{label}: {width}x{height} is not {'16:9' if variant == 'landscape' else '9:16'} (1.5% tolerance)")
                if kind == "videos":
                    if not math.isfinite(duration) or duration <= 0 or not math.isfinite(fps) or fps <= 0:
                        errors.append(f"{label}: readable positive duration and frame rate are required")
                    else:
                        video_info[variant] = (duration, fps)
            except (ValueError, KeyError, subprocess.SubprocessError) as exc:
                errors.append(f"{label}: cannot verify media: {exc}")

    if mode == "both-same" and len(video_info) == 2:
        left, right = video_info["landscape"], video_info["portrait"]
        tolerance = max(1 / left[1], 1 / right[1])
        if abs(left[0] - right[0]) > tolerance + 0.000001:
            errors.append(f"both-same: durations differ ({left[0]:.3f}s vs {right[0]:.3f}s); maximum is one frame ({tolerance:.4f}s)")

    for platform, entry in platforms.items():
        label = f"platforms.{platform}"
        if platform not in PLATFORMS:
            errors.append(f"{label}: unsupported platform")
        if not isinstance(entry, dict):
            errors.append(f"{label}: must be an object")
            continue
        for field in ("title", "description"):
            if not meaningful(entry.get(field)):
                errors.append(f"{label}.{field}: supply finished nonblank copy, with no TODO or example.invalid placeholder")
        for field in ("video", "thumbnail"):
            if field == "thumbnail" and waived_thumbnails:
                if field not in entry or entry[field] is not None:
                    errors.append(f"{label}.thumbnail: must be null when thumbnails are explicitly waived")
            elif entry.get(field) not in needed:
                errors.append(f"{label}.{field}: choose a required variant from {needed}")
        copy_path = file_reference(entry.get("copy_path"), label + ".copy_path")
        if copy_path:
            try:
                if not copy_path.read_text(encoding="utf-8").strip():
                    errors.append(f"{label}.copy_path: copy file is empty")
            except UnicodeError:
                errors.append(f"{label}.copy_path: must be UTF-8 text")
    if errors:
        print("Package incomplete:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Package verified: {len(needed)} video(s), {len(needed_thumbnails)} thumbnail(s), {len(platforms)} platform copy set(s).")
    if waived_thumbnails:
        print(f"Thumbnails waived by explicit user instruction: {thumbnail_waiver}")
    print("Technical checks passed; editorial, visual, and audio review still require the agent.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create a pending manifest without rendering or writing copy")
    init.add_argument("output_dir")
    init.add_argument("--topic", required=True)
    init.add_argument("--mode", choices=MODES, required=True)
    init.add_argument("--platforms", default=DEFAULT_PLATFORMS)
    init.add_argument("--source", action="append", required=True, help="Existing source file; repeat for multiple files")
    check = commands.add_parser("check", help="Read-only verification of a completed package; requires ffprobe")
    check.add_argument("manifest", help="Path to production.json")
    args = parser.parse_args()
    try:
        return check_package(args) if args.command == "check" else init_package(args) or 0
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
