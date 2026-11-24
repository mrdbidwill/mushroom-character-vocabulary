> **No advice about consumption.** This vocabulary reports how sources describe fungi. It is not a guide to eating, using or handling any fungus, and nothing here says whether any fungus is safe. Values about chemistry or toxicity are reported only as their source states them.

# Mushroom Character Vocabulary, release 1.1.0

Prepared 2026-11-24. A proposal for use. Nobody can declare a standard; adoption comes from use. Every part, character and value option is marked proposed.

Will Johnston, 2026-11-14: "The goal is to improve the accuracy of fungi data by providing tools to citizen scientists and others that make this goal easier."

## What is new in 1.1.0
Release 1.0.0 is unchanged and stays as published; this release is 1.0.0 plus what step 2 added. Nothing was removed and no identifier changed.
- **Definitions** (`definitions.csv`): 800 sourced records. Each names the entry it is for, the relation, the source, the page and, where the source's license allows it, the exact words.
  - Parts: cross-reference 2; defines 14; describes the group 3; narrower 5.
  - Characters: cross-reference 23; pointer 136; related 29; the quality it records 43; the structure it describes 131; the term it records 3.
  - Value options: cross-reference 3; defines 262; related 146.
  - Wording is quoted only from Kauffman 1918 (public domain in the United States), each quotation read from the page image. The Fungal Anatomy Ontology (FAO) and PubChem are pointers: an identifier and a name, no wording.
  - Entries with no record: 6 parts and 342 characters for which no source was found. Of the 1313 value options in the open list, 372 have a record; 151 were searched and no entry was found; 763 are answer words (Yes, No, Unknown, Not Tested, Other, None), not defined as words; 27 were not searched in step 2.
  - An old wording is a record of how a source used a word, not a statement of current science. A printing error is quoted as printed and named in the record's note.
- **Units** (`units.csv`): the unit of each of the 73 measurement characters with its identifier in the Units of Measurement Ontology (UO). 14 units set where 1.0.0 had none; 2 spore-range units given as µm in place of mm, as new versions.
- **Links** (`links.csv`): 52 links between characters and between value options: 'same as', 'close' and 'not the same'. Nothing is merged; both ends stay in the list.
- **Additions**: 1 character (partial veil present, with the four value options Yes, No, Unknown, Not Tested) and 72 value options from Kauffman's glossary, each with its evidence in `changes/changes_in_1.1.0.csv`. 77 new identifiers, MCV_0002168 to MCV_0002244.
- **References** (`references.csv`): 81 references, the ones of the shared references register that bear on this vocabulary. 16 name the characters they are cited for. 4 carry the notice "No advice about consumption." beside them because their subject includes eating or using fungi; they are listed for how they describe fungi.

| | |
|---|---|
| Identifiers | 2244 (MCV_0000001 to MCV_0002244) |
| Parts | 17 |
| Characters | 654 (638 in the open list, 16 under another source's license) |
| Value options | 1573 (1313 in the open list, 260 under another source's license) |
| Definition records | 800 |
| Units | 73 |
| Links | 52 |
| References | 81 |

## The identifiers
MCV_ and seven digits. The number means nothing: it is only the order in which an identifier was given. Written in full: https://w3id.org/mcv/MCV_0000001.
- An identifier is given once and never reused. It is never deleted: a retired one stays in the register with a pointer to what replaced it.
- The wording may change from release to release; the identifier does not.
- The register, identifiers.csv, is add-only. Each row says the release that first gave the identifier.

## License
CC0 1.0 Universal for the files of the open list, as in 1.0.0, except the UO identifiers and unit names (CC BY 4.0); see LICENSE.md.
- The quotations in `definitions.csv` are from Kauffman 1918, public domain in the United States.
- The UO identifiers and unit names in `units.csv` are from UO, CC BY 4.0, credited in `other_licenses/uo/`.
- `other_licenses/fungaltraits/` is unchanged from 1.0.0: its words keep their authors' license.
- `references.csv` lists works by title. A title is cited, not copied; each work keeps its own license.

## The files
- `parts.csv`, `characters.csv`, `value_options.csv` — the open list, as in 1.0.0, with the additions and the units of this release.
- `definitions.csv` — the definition records. `relation` says what the record is to its entry: for a value option, `defines` (the source's entry for that word and that part), `related` (an entry for the word for another part), `cross-reference`; for a character, `the structure it describes`, `the quality it records`, `the term it records`, `related`, `cross-reference`, `pointer` (PubChem); for a part, `defines`, `narrower`, `cross-reference`, `describes the group`. `part_definition_records` gives, for a character, the records of its part.
- `units.csv` — unit, UO identifier and UO name of each measurement character.
- `links.csv` — the links, each with its basis.
- `references.csv` — the references, with `cited_for_ids` and the notice where it applies.
- `changes/changes_in_1.1.0.csv` — every addition and unit change of this release, with its evidence. The two files of 1.0.0 are carried unchanged.
- `vocabulary.json` — the same list in one file, with definitions, units, links and references.
- `keys.csv`, `left_for_users.csv`, `sources.csv`, `other_licenses/` — as in 1.0.0; `sources.csv` adds the sources of step 2.
- `MANIFEST.json` — the counts and a checksum of every file.

## Credits
The first list: "Observation List: Characters With Taxonomic Value For Stipitate-Lamellate Mushrooms", Mushroom Observer species list 1417, used by its author's permission (see 1.0.0). Definitions: C. H. Kauffman, The Agaricaceae of Michigan (1918), scan of the New York Botanical Garden copy at the Internet Archive. Units: the Units of Measurement Ontology. Compiled by Will Johnston. Built with Claude (Anthropic).

> **No advice about consumption.** This vocabulary reports how sources describe fungi. It is not a guide to eating, using or handling any fungus, and nothing here says whether any fungus is safe. Values about chemistry or toxicity are reported only as their source states them.
