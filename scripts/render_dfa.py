#!/usr/bin/env python3
"""Compatibility entry point. Prefer render_automaton.py for all machine types.

Existing CLI commands and imports continue to use the same renderer.
"""

if __package__:
    from . import render_automaton as _renderer
else:
    import render_automaton as _renderer

HTML_TEMPLATE = _renderer.HTML_TEMPLATE
apply_grid_layout = _renderer.apply_grid_layout
auto_layout = _renderer.auto_layout
build_simulation_data = _renderer.build_simulation_data
compile_automaton = _renderer.compile_automaton
compute_node_radius_and_font = _renderer.compute_node_radius_and_font
generate_svg = _renderer.generate_svg
main = _renderer.main
normalize_symbol = _renderer.normalize_symbol
parse_and_normalize_symbols = _renderer.parse_and_normalize_symbols
sanitize_dom_id = _renderer.sanitize_dom_id

# Preserve the old public compiler name for existing Python callers.
compile_dfa = compile_automaton


if __name__ == "__main__":
    main()
