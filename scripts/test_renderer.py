"""Check canonical renderer entry points and legacy command compatibility."""

import contextlib
import io
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parent


class RendererEntryPointTests(unittest.TestCase):
    def setUp(self):
        self.spec = {
            "type": "epsilon_nfa",
            "alphabet": ["a"],
            "states": [
                {"id": "s", "x": 150, "y": 150, "is_start": True},
                {"id": "f", "x": 450, "y": 150, "is_accept": True},
            ],
            "transitions": [{"from": "s", "to": "f", "symbols": ["ε"]}],
        }

    def test_script_and_module_entry_points_render_epsilon_nfa_with_correct_default_title(self):
        # A missing canonical command or a DFA-only fallback title breaks this.
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            spec_path = out / "epsilon.json"
            spec_path.write_text(json.dumps(self.spec), encoding="utf-8")
            results = []
            commands = [
                ("canonical_script", [str(SCRIPTS / "render_automaton.py")]),
                ("legacy_script", [str(SCRIPTS / "render_dfa.py")]),
                ("canonical_module", ["-m", "scripts.render_automaton"]),
                ("legacy_module", ["-m", "scripts.render_dfa"]),
            ]
            for name, command in commands:
                with self.subTest(entry_point=name):
                    html, svg = out / (name + ".html"), out / (name + ".svg")
                    proc = subprocess.run(
                        [sys.executable, *command, "--spec", str(spec_path),
                         "--out", str(html), "--svg", str(svg)],
                        capture_output=True, text=True, encoding="utf-8", cwd=SCRIPTS.parent,
                    )
                    self.assertEqual(proc.returncode, 0, proc.stderr)
                    content = html.read_text(encoding="utf-8")
                    self.assertEqual(re.search(r"<h1>(.*?)</h1>", content).group(1), "Epsilon-NFA")
                    self.assertTrue(svg.exists())
                    results.append(content)
            if len(results) == len(commands):
                for content in results[1:]:
                    self.assertEqual(results[0], content)

    def test_legacy_compiler_api_remains_compatible_with_canonical_api(self):
        # Broken old imports or an incompatible forwarding signature break this.
        self.assertTrue((SCRIPTS / "render_automaton.py").is_file())
        sys.path.insert(0, str(SCRIPTS))
        try:
            import render_automaton
            import render_dfa
            with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
                out = Path(directory)
                new, old = out / "new.html", out / "old.html"
                render_automaton.compile_automaton(self.spec, str(new))
                render_dfa.compile_dfa(self.spec, str(old))
                self.assertEqual(new.read_bytes(), old.read_bytes())
                data = render_dfa.build_simulation_data(self.spec)
                self.assertEqual(data["epsilon_map"]["s"], ["f"])
                self.assertEqual(data["accept_states"], ["f"])
        finally:
            sys.path.pop(0)


if __name__ == "__main__":
    unittest.main()
