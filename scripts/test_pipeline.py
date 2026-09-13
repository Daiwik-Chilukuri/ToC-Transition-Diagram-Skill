#!/usr/bin/env python3
"""
test_pipeline.py
Automated end-to-end verification harness for automata-pipeline.
Validates:
  Stage 1: JSON Schema & Mathematical Integrity Validation across all specs
  Stage 2: Batch HTML & SVG Compilation via render_dfa.py
  Stage 3: Simulator Logic Verification across all test_cases (DFA and NFA/ε-NFA)
  Stage 4: CLI Interface Verification of render_dfa.py
  Stage 5: Clean Tabular Reporting & Exit Code

Zero third-party dependencies (Python 3 stdlib only).
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Safe Unicode output on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# ANSI Color formatting
USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")

def color(text: str, code: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"

def green(text: str) -> str: return color(text, "92")
def red(text: str) -> str: return color(text, "91")
def yellow(text: str) -> str: return color(text, "93")
def cyan(text: str) -> str: return color(text, "96")
def bold(text: str) -> str: return color(text, "1")

# Ensure scripts directory is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    from render_dfa import (
        build_simulation_data,
        compile_dfa,
        parse_and_normalize_symbols,
        auto_layout,
    )
except ImportError as err:
    print(f"Error importing render_dfa: {err}", file=sys.stderr)
    sys.exit(1)


class StageResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.duration = 0.0
        self.errors = []

    def record_pass(self):
        self.passed += 1

    def record_fail(self, error_msg: str):
        self.failed += 1
        self.errors.append(error_msg)

    def record_skip(self):
        self.skipped += 1


# -----------------------------------------------------------------------------
# Stage 1: JSON Schema & Mathematical Integrity Validation
# -----------------------------------------------------------------------------
def validate_spec_integrity(spec_path: Path) -> list[str]:
    """Validates the formal mathematical quintuple and schema of a spec."""
    errors = []
    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return [f"JSON parse error: {e}"]

    if not isinstance(data, dict):
        return ["Root element must be a JSON object"]

    # States validation (Q)
    states = data.get("states")
    if not isinstance(states, list) or len(states) == 0:
        errors.append("Missing or empty 'states' list")
        return errors

    state_ids = set()
    start_count = 0
    for idx, s in enumerate(states):
        if not isinstance(s, dict):
            errors.append(f"State at index {idx} is not an object")
            continue
        sid = s.get("id")
        if not sid or not isinstance(sid, str):
            errors.append(f"State at index {idx} missing valid string 'id'")
        elif sid in state_ids:
            errors.append(f"Duplicate state id '{sid}'")
        else:
            state_ids.add(sid)

        if s.get("is_start", False):
            start_count += 1

    if start_count != 1:
        errors.append(f"Start state count is {start_count}; expected exactly 1")

    # Alphabet validation (Sigma)
    alphabet_raw = data.get("alphabet")
    if not isinstance(alphabet_raw, list) or len(alphabet_raw) == 0:
        errors.append("Missing or empty 'alphabet' list")
        alphabet = set()
    else:
        alphabet = set(str(sym) for sym in alphabet_raw)

    # Transitions validation (delta)
    transitions = data.get("transitions")
    if not isinstance(transitions, list):
        errors.append("Missing 'transitions' list")
    else:
        for idx, t in enumerate(transitions):
            if not isinstance(t, dict):
                errors.append(f"Transition at index {idx} is not an object")
                continue
            src = t.get("from")
            if src not in state_ids:
                errors.append(f"Transition {idx}: source '{src}' not in states")

            dst_raw = t.get("to")
            dst_list = dst_raw if isinstance(dst_raw, list) else [dst_raw]
            for target in dst_list:
                if target not in state_ids:
                    errors.append(f"Transition {idx}: target '{target}' not in states")

            symbols = parse_and_normalize_symbols(t.get("symbols", []))
            if not symbols:
                errors.append(f"Transition {idx}: no symbols defined")
            for sym in symbols:
                if sym != "ε" and sym not in alphabet:
                    errors.append(f"Transition {idx}: symbol '{sym}' not in alphabet {alphabet}")

    # Test cases validation (if present)
    test_cases = data.get("test_cases")
    if test_cases is not None:
        if not isinstance(test_cases, list):
            errors.append("'test_cases' must be a list")
        else:
            for idx, tc in enumerate(test_cases):
                if not isinstance(tc, dict):
                    errors.append(f"Test case {idx} is not an object")
                    continue
                if "input" not in tc or not isinstance(tc["input"], str):
                    errors.append(f"Test case {idx} missing string 'input'")
                if "expected" not in tc or not isinstance(tc["expected"], bool):
                    errors.append(f"Test case {idx} missing boolean 'expected'")

    return errors


def run_stage_1(spec_files: list[Path], verbose: bool) -> StageResult:
    result = StageResult("Stage 1: JSON Schema & Integrity Validation")
    t0 = time.time()
    print(f"\n{bold('Stage 1:')} JSON Schema & Mathematical Integrity Validation across {len(spec_files)} specs")

    for p in spec_files:
        try:
            rel_path = p.relative_to(REPO_ROOT)
        except ValueError:
            rel_path = p
        errs = validate_spec_integrity(p)
        if not errs:
            result.record_pass()
            if verbose:
                print(f"  {green('✓')} {rel_path} (valid quintuple)")
        else:
            result.record_fail(f"{rel_path}: {'; '.join(errs)}")
            print(f"  {red('✗')} {rel_path}:")
            for e in errs:
                print(f"      - {e}")

    result.duration = time.time() - t0
    status_str = green(f"{result.passed} passed") if result.failed == 0 else red(f"{result.failed} failed")
    print(f"  Result: {status_str} in {result.duration:.2f}s")
    return result


# -----------------------------------------------------------------------------
# Stage 2: Batch HTML & SVG Compilation
# -----------------------------------------------------------------------------
def verify_compiled_output(html_path: Path, svg_path: Path) -> list[str]:
    """Verifies that generated HTML and SVG files satisfy structural constraints."""
    errors = []
    if not html_path.exists():
        return [f"HTML artifact not created: {html_path}"]

    html_size = html_path.stat().st_size
    if html_size < 5120:
        errors.append(f"HTML artifact size {html_size} bytes is < 5 KB")

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f"Failed to read HTML artifact: {e}"]

    # Required markers
    required_html_markers = [
        "<!DOCTYPE html>",
        "<svg",
        "</svg>",
        "const DFA_SPEC =",
        "function stepSimulation",
        "function evaluateFinal",
        "class=\"tape-display\"",
    ]
    for marker in required_html_markers:
        if marker not in content:
            errors.append(f"HTML missing required marker: '{marker}'")

    if svg_path.exists():
        svg_size = svg_path.stat().st_size
        if svg_size < 500:
            errors.append(f"SVG artifact size {svg_size} bytes is < 500 B")
        try:
            with open(svg_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
            for marker in ["<svg", "</svg>", "<circle", "<text"]:
                if marker not in svg_content:
                    errors.append(f"SVG missing required element: '{marker}'")
        except Exception as e:
            errors.append(f"Failed to read SVG artifact: {e}")
    else:
        errors.append(f"SVG artifact not created: {svg_path}")

    return errors


def run_stage_2(spec_files: list[Path], python_exe: str, renderer_path: Path, verbose: bool, fast: bool) -> StageResult:
    result = StageResult("Stage 2: Batch HTML & SVG Compilation")
    t0 = time.time()
    mode_str = " (fast in-process mode)" if fast else " (subprocess isolation)"
    print(f"\n{bold('Stage 2:')} Batch HTML & SVG Compilation across {len(spec_files)} specs{mode_str}")

    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)

        for p in spec_files:
            try:
                rel_path = p.relative_to(REPO_ROOT)
            except ValueError:
                rel_path = p
            base_name = p.stem
            out_html = tmp_dir / f"{base_name}.html"
            out_svg = tmp_dir / f"{base_name}.svg"

            if fast:
                # Fast mode: in-process compilation
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        spec_data = json.load(f)
                    spec_data = auto_layout(spec_data, "auto")
                    compile_dfa(spec_data, str(out_html), str(out_svg))
                    errs = verify_compiled_output(out_html, out_svg)
                except Exception as e:
                    errs = [f"Compilation error: {e}"]
            else:
                # Standard mode: full subprocess execution
                cmd = [
                    python_exe,
                    str(renderer_path),
                    "--spec", str(p),
                    "--out", str(out_html),
                    "--svg", str(out_svg),
                ]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                if proc.returncode != 0:
                    errs = [f"render_dfa.py exited with code {proc.returncode}: {proc.stderr.strip()}"]
                else:
                    errs = verify_compiled_output(out_html, out_svg)

            if not errs:
                result.record_pass()
                if verbose:
                    h_sz = out_html.stat().st_size / 1024
                    print(f"  {green('✓')} {rel_path} -> HTML ({h_sz:.1f} KB), SVG valid")
            else:
                result.record_fail(f"{rel_path}: {'; '.join(errs)}")
                print(f"  {red('✗')} {rel_path}:")
                for e in errs:
                    print(f"      - {e}")

        # Smoke subprocess test if fast mode was used
        if fast and spec_files:
            sample_spec = spec_files[0]
            smoke_html = tmp_dir / "smoke.html"
            cmd = [python_exe, str(renderer_path), "--spec", str(sample_spec), "--out", str(smoke_html)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                result.record_fail(f"Smoke CLI test failed: {proc.stderr}")

    result.duration = time.time() - t0
    status_str = green(f"{result.passed} passed") if result.failed == 0 else red(f"{result.failed} failed")
    print(f"  Result: {status_str} in {result.duration:.2f}s")
    return result


# -----------------------------------------------------------------------------
# Stage 3: Simulator Logic Verification
# -----------------------------------------------------------------------------
def py_simulate_automaton(sim_data: dict, input_str: str) -> bool:
    """
    Mathematical simulator for both DFAs and NFAs with epsilon-transitions.
    Computes subset powerset propagation with epsilon-closures.
    """
    trans_map = sim_data.get("transition_map", {})
    eps_map = sim_data.get("epsilon_map", {})
    accept_states = set(sim_data.get("accept_states", []))

    def get_eps(q):
        if q in eps_map and eps_map[q]:
            return eps_map[q]
        return trans_map.get(f"{q},ε", [])

    def eps_closure(states):
        closure = set(states)
        stack = list(states)
        while stack:
            curr = stack.pop()
            for nxt in get_eps(curr):
                if nxt not in closure:
                    closure.add(nxt)
                    stack.append(nxt)
        return closure

    start_st = sim_data.get("start_state")
    active = eps_closure([start_st]) if start_st is not None else set()

    for sym in input_str:
        next_active = set()
        for q in active:
            targets = trans_map.get(f"{q},{sym}", [])
            for tgt in targets:
                next_active.update(eps_closure([tgt]))
        active = next_active

    return bool(active & accept_states)


def run_stage_3(spec_files: list[Path], verbose: bool) -> StageResult:
    result = StageResult("Stage 3: Simulator Logic Verification")
    t0 = time.time()
    total_test_cases = 0
    passed_test_cases = 0
    failed_test_cases = 0

    print(f"\n{bold('Stage 3:')} Simulator Logic Verification across all test cases")

    for p in spec_files:
        try:
            rel_path = p.relative_to(REPO_ROOT)
        except ValueError:
            rel_path = p
        try:
            with open(p, "r", encoding="utf-8") as f:
                spec = json.load(f)
        except Exception as e:
            result.record_fail(f"{rel_path}: JSON load error {e}")
            continue

        test_cases = spec.get("test_cases", [])
        sim_data = build_simulation_data(spec)

        if not test_cases:
            # Spec has no test_cases: verify sample_input doesn't crash
            sample_inp = spec.get("sample_input", "")
            try:
                _ = py_simulate_automaton(sim_data, sample_inp)
                result.record_pass()
                if verbose:
                    print(f"  {green('✓')} {rel_path} (no test_cases, sample_input '{sample_inp}' simulated)")
            except Exception as e:
                result.record_fail(f"{rel_path}: sample_input simulation failed: {e}")
            continue

        spec_failures = []
        for idx, tc in enumerate(test_cases):
            inp = tc.get("input", "")
            expected = tc.get("expected", False)
            total_test_cases += 1
            got = py_simulate_automaton(sim_data, inp)

            if got == expected:
                passed_test_cases += 1
            else:
                failed_test_cases += 1
                spec_failures.append(f"case {idx} inp='{inp}': expected {expected}, got {got}")

        if not spec_failures:
            result.record_pass()
            if verbose:
                print(f"  {green('✓')} {rel_path} ({len(test_cases)}/{len(test_cases)} test cases passed)")
        else:
            result.record_fail(f"{rel_path}: {len(spec_failures)} failed cases ({'; '.join(spec_failures[:3])})")
            print(f"  {red('✗')} {rel_path}:")
            for f_msg in spec_failures:
                print(f"      - {f_msg}")

    result.duration = time.time() - t0
    tc_summary = f"{passed_test_cases}/{total_test_cases} test cases passed"
    status_str = green(tc_summary) if failed_test_cases == 0 else red(f"{failed_test_cases} test cases failed")
    print(f"  Result: {status_str} across {result.passed} specs in {result.duration:.2f}s")
    return result


# -----------------------------------------------------------------------------
# Stage 4: CLI Interface Verification
# -----------------------------------------------------------------------------
def run_stage_4(python_exe: str, renderer_path: Path, sample_spec_path: Path, verbose: bool, fast: bool) -> StageResult:
    result = StageResult("Stage 4: CLI Interface Verification")
    t0 = time.time()
    print(f"\n{bold('Stage 4:')} CLI Interface Verification of render_dfa.py")

    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)

        # Test 1: --help
        res = subprocess.run([python_exe, str(renderer_path), "--help"], capture_output=True, text=True)
        if res.returncode == 0 and "--spec" in res.stdout and "--out" in res.stdout:
            result.record_pass()
            if verbose: print(f"  {green('✓')} CLI --help flag returned code 0 with expected flags")
        else:
            result.record_fail(f"--help failed: rc={res.returncode}, out={res.stdout}")

        # Test 2: Missing required arguments
        res = subprocess.run([python_exe, str(renderer_path)], capture_output=True, text=True)
        if res.returncode != 0:
            result.record_pass()
            if verbose: print(f"  {green('✓')} Missing arguments correctly rejected with code {res.returncode}")
        else:
            result.record_fail("Missing arguments unexpectedly succeeded with code 0")

        # Test 3: Non-existent spec file
        res = subprocess.run([
            python_exe, str(renderer_path),
            "--spec", "non_existent_automaton_spec_xyz.json",
            "--out", str(tmp_dir / "out.html")
        ], capture_output=True, text=True)
        if res.returncode != 0:
            result.record_pass()
            if verbose: print(f"  {green('✓')} Non-existent spec correctly rejected with code {res.returncode}")
        else:
            result.record_fail("Non-existent spec unexpectedly returned code 0")

        # Test 4: Layout engine variations
        layouts = ["linear", "circle", "grid_2x3"] if fast else ["auto", "linear", "circle", "grid_2x2", "grid_2x3"]
        for l_opt in layouts:
            out_html = tmp_dir / f"layout_{l_opt}.html"
            out_svg = tmp_dir / f"layout_{l_opt}.svg"
            cmd = [
                python_exe, str(renderer_path),
                "--spec", str(sample_spec_path),
                "--out", str(out_html),
                "--svg", str(out_svg),
                "--layout", l_opt
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0 and out_html.exists() and out_svg.exists():
                result.record_pass()
                if verbose: print(f"  {green('✓')} Layout '--layout {l_opt}' generated HTML and SVG cleanly")
            else:
                result.record_fail(f"Layout '{l_opt}' failed: rc={res.returncode}, err={res.stderr.strip()}")

        # Test 5: Optional --svg omission
        out_no_svg = tmp_dir / "no_svg.html"
        cmd = [python_exe, str(renderer_path), "--spec", str(sample_spec_path), "--out", str(out_no_svg)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and out_no_svg.exists():
            result.record_pass()
            if verbose: print(f"  {green('✓')} Command succeeded with --svg omitted")
        else:
            result.record_fail(f"Omission of --svg failed: rc={res.returncode}")

    result.duration = time.time() - t0
    status_str = green(f"{result.passed} passed") if result.failed == 0 else red(f"{result.failed} failed")
    print(f"  Result: {status_str} in {result.duration:.2f}s")
    return result


# -----------------------------------------------------------------------------
# Stage 5: Summary Report & Runner Orchestration
# -----------------------------------------------------------------------------
def print_summary_table(results: list[StageResult], total_time: float) -> int:
    header = f"{bold('Stage'):<45} {bold('Passed'):>8} {bold('Failed'):>8} {bold('Skipped'):>8} {bold('Time'):>9}"
    sep = "-" * 82
    print(f"\n{bold(cyan('=' * 82))}")
    print(f"{bold(cyan('  AUTOMATA PIPELINE VERIFICATION SUITE — SUMMARY REPORT'))}")
    print(f"{bold(cyan('=' * 82))}")
    print(f"  {header}")
    print(f"  {sep}")

    total_passed = 0
    total_failed = 0
    total_skipped = 0

    for r in results:
        total_passed += r.passed
        total_failed += r.failed
        total_skipped += r.skipped

        p_str = f"{r.passed:>8}"
        f_str = f"{r.failed:>8}"
        s_str = f"{r.skipped:>8}"
        pass_col = green(p_str) if r.passed > 0 else p_str
        fail_col = red(f_str) if r.failed > 0 else f_str
        skip_col = yellow(s_str) if r.skipped > 0 else s_str
        time_col = f"{r.duration:>8.2f}s"

        print(f"  {r.name:<45} {pass_col} {fail_col} {skip_col}  {time_col}")

    print(f"  {sep}")
    print(f"  {bold('Total Suite Execution Time:')} {total_time:.2f}s")
    print(f"{bold(cyan('=' * 82))}")

    if total_failed == 0:
        print(f"  {bold(green('FINAL VERDICT: ALL TESTS PASSED (100% SUCCESS)'))}")
        print(f"{bold(cyan('=' * 82))}\n")
        return 0
    else:
        print(f"  {bold(red(f'FINAL VERDICT: VERIFICATION FAILED ({total_failed} FAILING CHECKS)'))}")
        print(f"{bold(cyan('=' * 82))}\n")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Automata Pipeline automated verification harness (Milestone 4)"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose per-spec and per-test logs")
    parser.add_argument("--specs-dir", default=str(REPO_ROOT / "specs"), help="Path to specs directory")
    parser.add_argument("--examples-dir", default=str(SCRIPTS_DIR / "examples"), help="Path to examples directory")
    parser.add_argument("--fast", action="store_true", help="Fast mode: in-process compilation and smoke CLI checks")
    parser.add_argument("--stage", type=int, choices=[1, 2, 3, 4], help="Run only a specific stage (1-4)")

    args = parser.parse_args()

    python_exe = sys.executable
    renderer_path = SCRIPTS_DIR / "render_dfa.py"

    if not renderer_path.exists():
        print(f"Error: Renderer script not found at {renderer_path}", file=sys.stderr)
        sys.exit(1)

    specs_dir = Path(args.specs_dir)
    examples_dir = Path(args.examples_dir)

    spec_files = []
    seen = set()
    if specs_dir.exists():
        for p in sorted(specs_dir.glob("*.json")):
            resolved = p.resolve()
            if resolved not in seen:
                seen.add(resolved)
                spec_files.append(p)
    if examples_dir.exists():
        for p in sorted(examples_dir.glob("*.json")):
            resolved = p.resolve()
            if resolved not in seen:
                seen.add(resolved)
                spec_files.append(p)

    if not spec_files:
        print(f"Error: No spec files found in {specs_dir} or {examples_dir}", file=sys.stderr)
        sys.exit(1)

    # Pick representative spec for CLI tests
    sample_spec = next((s for s in spec_files if "fig1_10_union" in s.name or "fig1_10_product_union" in s.name), spec_files[0])

    print(f"{bold('Automata Pipeline Automated Test Runner')}")
    print(f"Discovered {len(spec_files)} machine specifications across:")
    print(f"  - Specs:    {specs_dir}")
    print(f"  - Examples: {examples_dir}")

    total_start = time.time()
    results = []

    if args.stage is None or args.stage == 1:
        results.append(run_stage_1(spec_files, args.verbose))
    if args.stage is None or args.stage == 2:
        results.append(run_stage_2(spec_files, python_exe, renderer_path, args.verbose, args.fast))
    if args.stage is None or args.stage == 3:
        results.append(run_stage_3(spec_files, args.verbose))
    if args.stage is None or args.stage == 4:
        results.append(run_stage_4(python_exe, renderer_path, sample_spec, args.verbose, args.fast))

    total_duration = time.time() - total_start
    exit_code = print_summary_table(results, total_duration)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
