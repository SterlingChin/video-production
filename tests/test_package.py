"""Exercise the package CLI with tiny, real media; no Python dependencies."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills" / "video-production" / "scripts" / "package.py"


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for tool in ("ffmpeg", "ffprobe"):
            if not shutil.which(tool):
                raise RuntimeError(f"Install FFmpeg with {tool} on PATH to run media tests")
        cls.media_directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.media_directory.cleanup)
        cls.media = Path(cls.media_directory.name)
        for name, size, duration in (
            ("landscape", "160x90", "1"),
            ("portrait", "90x160", "1"),
            ("portrait-long", "90x160", "1.5"),
            ("square", "90x90", "1"),
        ):
            cls.ffmpeg(
                "-f", "lavfi", "-i", f"color=c=navy:s={size}:r=10",
                "-t", duration, "-an", "-c:v", "mpeg4", "-pix_fmt", "yuv420p",
                str(cls.media / f"{name}.mp4"),
            )
            if name != "portrait-long":
                cls.ffmpeg(
                    "-f", "lavfi", "-i", f"color=c=navy:s={size}",
                    "-frames:v", "1", "-threads", "1",
                    str(cls.media / f"{name}.png"),
                )

    @staticmethod
    def ffmpeg(*arguments):
        result = subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", *arguments],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode:
            raise RuntimeError(f"Cannot create test media: {result.stderr}")

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output = Path(self.directory.name) / "package"
        self.manifest = self.output / "production.json"

    def run_helper(self, *arguments):
        # An unrelated cwd also exercises installed-skill invocation by absolute path.
        return subprocess.run(
            [sys.executable, str(HELPER), *map(str, arguments)],
            cwd=self.directory.name, capture_output=True, text=True, timeout=30,
        )

    def initialize(self, mode="both-same"):
        return self.run_helper(
            "init", self.output, "--topic", "A practical editing walkthrough",
            "--mode", mode, "--source", self.media / "landscape.mp4",
            "--platforms", "youtube,youtube-shorts,instagram",
        )

    def save(self, data):
        self.manifest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def complete_package(self):
        result = self.initialize()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        for kind, suffix in (("videos", "mp4"), ("thumbnails", "png")):
            for variant, entry in data[kind].items():
                target = self.output / entry["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(self.media / f"{variant}.{suffix}", target)
        for name, entry in data["platforms"].items():
            entry["title"] = "Make an edit that preserves the story"
            entry["description"] = "A walkthrough of keeping context while removing repeated takes."
            target = self.output / entry["copy_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(entry["title"] + "\n\n" + entry["description"] + "\n", encoding="utf-8")
        self.save(data)
        return data

    def snapshot(self):
        return {
            path.relative_to(self.output): path.read_bytes()
            for path in self.output.rglob("*") if path.is_file()
        }

    def test_complete_both_same_passes_without_changing_files(self):
        self.complete_package()
        before = self.snapshot()
        result = self.run_helper("check", self.manifest)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 video(s), 2 thumbnail(s), 3 platform copy set(s)", result.stdout)
        self.assertIn("editorial, visual, and audio review", result.stdout)
        self.assertEqual(self.snapshot(), before)

    def test_missing_video_or_thumbnail_fails_with_the_asset_name(self):
        data = self.complete_package()
        for kind in ("videos", "thumbnails"):
            with self.subTest(kind=kind):
                target = self.output / data[kind]["portrait"]["path"]
                original = target.read_bytes()
                target.unlink()
                before = self.snapshot()
                result = self.run_helper("check", self.manifest)
                self.assertEqual(result.returncode, 1)
                self.assertIn(f"{kind}.portrait.path: missing file", result.stderr)
                self.assertEqual(self.snapshot(), before)
                target.write_bytes(original)

    def test_missing_description_fails_even_when_copy_file_exists(self):
        data = self.complete_package()
        del data["platforms"]["youtube-shorts"]["description"]
        self.save(data)
        result = self.run_helper("check", self.manifest)
        self.assertEqual(result.returncode, 1)
        self.assertIn("platforms.youtube-shorts.description: supply finished nonblank copy", result.stderr)

    def test_incorrect_video_and_thumbnail_aspects_are_rejected(self):
        data = self.complete_package()
        for kind, suffix in (("videos", "mp4"), ("thumbnails", "png")):
            with self.subTest(kind=kind):
                target = self.output / data[kind]["portrait"]["path"]
                shutil.copyfile(self.media / f"square.{suffix}", target)
                result = self.run_helper("check", self.manifest)
                self.assertEqual(result.returncode, 1)
                self.assertIn(f"{kind}.portrait: 90x90 is not 9:16", result.stderr)
                shutil.copyfile(self.media / f"portrait.{suffix}", target)

    def test_different_durations_require_both_distinct(self):
        data = self.complete_package()
        shutil.copyfile(self.media / "portrait-long.mp4", self.output / data["videos"]["portrait"]["path"])
        result = self.run_helper("check", self.manifest)
        self.assertEqual(result.returncode, 1)
        self.assertIn("both-same: durations differ (1.000s vs 1.500s)", result.stderr)
        data["mode"] = "both-distinct"
        self.save(data)
        result = self.run_helper("check", self.manifest)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_explicit_thumbnail_waiver_passes_and_reports_the_instruction(self):
        data = self.complete_package()
        instruction = "Skip thumbnails for this delivery."
        data["waivers"] = {"thumbnails": instruction}
        data["required_outputs"]["thumbnails"] = []
        for entry in data["platforms"].values():
            entry["thumbnail"] = None
        shutil.rmtree(self.output / "thumbnails")
        self.save(data)
        result = self.run_helper("check", self.manifest)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 video(s), 0 thumbnail(s)", result.stdout)
        self.assertIn(f"Thumbnails waived by explicit user instruction: {instruction}", result.stdout)

    def test_placeholder_waiver_cannot_hide_missing_thumbnails(self):
        data = self.complete_package()
        data["waivers"] = {"thumbnails": "TODO: ask for an exception"}
        shutil.rmtree(self.output / "thumbnails")
        self.save(data)
        result = self.run_helper("check", self.manifest)
        self.assertEqual(result.returncode, 1)
        self.assertIn("waivers.thumbnails: quote the exact explicit user instruction", result.stderr)
        self.assertIn("thumbnails.landscape.path: missing file", result.stderr)

    def test_init_never_overwrites_an_existing_manifest(self):
        result = self.initialize()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(self.output.iterdir()), {self.manifest})
        original = self.manifest.read_bytes()
        result = self.initialize(mode="vertical")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Refusing to overwrite", result.stderr)
        self.assertEqual(self.manifest.read_bytes(), original)
        self.assertEqual(set(self.output.iterdir()), {self.manifest})


if __name__ == "__main__":
    unittest.main()
