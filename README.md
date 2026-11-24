# Mushroom Character Vocabulary

> **No advice about consumption.** This vocabulary reports how sources describe fungi. It is not a guide to eating, using or handling any fungus, and nothing here says whether any fungus is safe. Values about chemistry or toxicity are reported only as their source states them.

A list of the characters used to describe mushrooms: the parts of a mushroom, the characters of each part, and the value options of each character. Every one has a permanent identifier. A proposal for use: every entry is marked proposed.

> "The goal is to improve the accuracy of fungi data by providing tools to citizen scientists and others that make this goal easier." (Will Johnston, 2026-11-14)

## Current release: 1.1.0

- Files: [`releases/1.1.0/`](releases/1.1.0/). Start with its [README](releases/1.1.0/README.md).
- 2244 identifiers, MCV_0000001 to MCV_0002244: 17 parts, 654 characters, 1573 value options. New in 1.1.0: 800 definition records, units for 73 measurement characters, 52 links, 81 references, 1 character and 76 value options (MCV_0002168 to MCV_0002244). Release 1.0.0 is unchanged.
- Identifiers: `https://w3id.org/mcv/MCV_` and seven digits, for example https://w3id.org/mcv/MCV_0000026. Each leads to a page for that part, character or value option. The address is registered at w3id.org (live since 2026-11-23) and redirects to the pages at https://mrdbidwill.github.io/mushroom-character-vocabulary/.
- Archive and DOI (Zenodo): release 1.1.0 [10.5281/zenodo.24513196](https://doi.org/10.5281/zenodo.24513196); all releases [10.5281/zenodo.24465418](https://doi.org/10.5281/zenodo.24465418).
- Checksums: every file of the release is listed with its SHA-256 in [`MANIFEST.json`](releases/1.1.0/MANIFEST.json).

## Earlier releases

- 1.0.0 (2026-11-23): [`releases/1.0.0/`](releases/1.0.0/), DOI [10.5281/zenodo.24465419](https://doi.org/10.5281/zenodo.24465419).

## What is in this repository

| Path | What it is |
|---|---|
| `releases/1.1.0/`, `releases/1.0.0/` | The releases, each exactly as built. Never edited after publication; a correction is a new release. |
| `releases/identifiers.csv` | The register of identifiers. Add-only: an identifier is never reused or deleted. |
| `releases/build_release.py` | The script that built the release from the register, the rules and the working files of the MRDBID export. Published so the build can be read; the working files it reads are not in this repository, so it does not run from here. |
| `releases/build_release_1_1_0.py` | The script that built release 1.1.0 from release 1.0.0 and the working files of step 2. Published so the build can be read; its working files are not in this repository, so it does not run from here. |
| `releases/release_rules.json` | The rules the script applies. |
| `tools/build_pages.py` | Builds the identifier pages in `docs/` from a release. |
| `docs/` | The identifier pages, served by GitHub Pages. |

## Licenses

- The open list of each release, the register and the rules: CC0 1.0 Universal. See each release's `LICENSE.md` and [`LICENSE.md`](LICENSE.md).
- `releases/*/other_licenses/`: the words of other sources, under those sources' licenses, as stated in each folder. Not CC0.
- Release 1.1.0, `units.csv`: the UO identifiers and unit names are from the Units of Measurement Ontology, CC BY 4.0, credited in `releases/1.1.0/other_licenses/uo/`. Not CC0.
- The scripts (`releases/build_release.py`, `releases/build_release_1_1_0.py`, `tools/build_pages.py`): MIT License. See [`LICENSE.md`](LICENSE.md).
- The pages in `docs/` show the release's words under the same licenses as the release files they come from; each page names its license.

## Credits

Compiled by Will Johnston. Sources and credits: each release's README and `sources.csv`. Built with Claude (Anthropic).

> **No advice about consumption.** This vocabulary reports how sources describe fungi. It is not a guide to eating, using or handling any fungus, and nothing here says whether any fungus is safe. Values about chemistry or toxicity are reported only as their source states them.
