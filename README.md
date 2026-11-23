# Mushroom Character Vocabulary

A list of the characters used to describe mushrooms: the parts of a mushroom, the characters of each part, and the value options of each character. Every one has a permanent identifier. A proposal for use: every entry is marked proposed.

> "The goal is to improve the accuracy of fungi data by providing tools to citizen scientists and others that make this goal easier." (Will Johnston, 2026-11-14)

## Current release: 1.0.0

- Files: [`releases/1.0.0/`](releases/1.0.0/). Start with its [README](releases/1.0.0/README.md).
- 2167 identifiers, MCV_0000001 to MCV_0002167: 17 parts, 653 characters, 1497 value options.
- Identifiers: `https://w3id.org/mcv/MCV_` and seven digits, for example https://w3id.org/mcv/MCV_0000026. Each leads to a page for that part, character or value option.
- Archive and DOI: (added when the archive is made)
- Checksums: every file of the release is listed with its SHA-256 in [`MANIFEST.json`](releases/1.0.0/MANIFEST.json).

## What is in this repository

| Path | What it is |
|---|---|
| `releases/1.0.0/` | Release 1.0.0, exactly as built. Never edited after publication; a correction is a new release. |
| `releases/identifiers.csv` | The register of identifiers. Add-only: an identifier is never reused or deleted. |
| `releases/build_release.py` | The script that built the release from the register, the rules and the working files of the MRDBID export. Published so the build can be read; the working files it reads are not in this repository, so it does not run from here. |
| `releases/release_rules.json` | The rules the script applies. |
| `tools/build_pages.py` | Builds the identifier pages in `docs/` from a release. |
| `docs/` | The identifier pages, served by GitHub Pages. |

## Licenses

- The open list of each release, the register and the rules: CC0 1.0 Universal. See each release's `LICENSE.md` and [`LICENSE.md`](LICENSE.md).
- `releases/*/other_licenses/`: the words of other sources, under those sources' licenses, as stated in each folder. Not CC0.
- The scripts (`releases/build_release.py`, `tools/build_pages.py`): MIT License. See [`LICENSE.md`](LICENSE.md).
- The pages in `docs/` show the release's words under the same licenses as the release files they come from; each page names its license.

## Credits

Compiled by Will Johnston. Sources and credits: each release's README and `sources.csv`. Built with Claude (Anthropic).
