# Mushroom Character Vocabulary, release 1.0.0

Prepared 2026-11-23. A proposal for use. Nobody can declare a standard; adoption comes from use. Every part, character and value option is marked proposed.

Will Johnston, 2026-11-14: "The goal is to improve the accuracy of fungi data by providing tools to citizen scientists and others that make this goal easier."

## What this is
A list of the characters used to describe mushrooms: the parts of a mushroom, the characters of each part, and the
value options of each character. Every one has a permanent identifier. The list is the whole character list of the
MRDBID database as exported on 2026-11-19, rebuilt against the list it was first parsed from, with the spelling
settled and every character named in United States English and in the scientific (Latin) form.

| | |
|---|---|
| Identifiers | 2167 (MCV_0000001 to MCV_0002167) |
| Parts | 17 |
| Characters | 653 (637 in the open list, 16 under another source's license) |
| Value options | 1497 (1237 in the open list, 260 under another source's license) |
| Character names that differ between English and Latin | 238 |
| Characters of a chemical compound with a registry number | 136 |

## The identifiers
MCV_ and seven digits. The number means nothing: it is only the order in which an identifier was given. Written in full: https://w3id.org/mcv/MCV_0000001.
- An identifier is given once and never reused. It is never deleted: a retired one stays in the register with a pointer to what replaced it.
- An identifier names a part, a character or a value option of one character. A value option used by several characters has one identifier for each of them, so that each character can carry its own description of it (Will, 2026-11-19 10:51, on the description of such a value option: "Each character gets its own").
- The wording may change from release to release; the identifier does not. The words as written stay on record beside the words shown.
- The register, identifiers.csv, is add-only. It is kept beside the folder of the release, with build_release.py and release_rules.json. build_release.py keeps every identifier it finds there and gives the next number to anything new.
- A thing that has no key in the MRDBID database is keyed in the register in another way: a new character by the label the rebuilt list gave it (NEW-1, NEW-2), an added value option by the key of its character and the letters of its name as first given. If such a name is changed in a later release, the rules of that release carry the identifier over; it is not given a new one.

## License
CC0 1.0 Universal for the files of the open list. The open list is Will Johnston's own compilation. Most of its characters were parsed from the first list, used by its author's permission of 2026-11-13. His words: "You've got my blessing to do as you wish and how you best see things to be presented." He named no license; that his permission covers a CC0 release is Will Johnston's decision of 2026-11-20 and 2026-11-22. The sentences of the first list are not carried in this release. Where words of that list are the reason for a change, or for a topic left to users, they are quoted there, a short sentence or a phrase at a time. Words taken from a source that has a license of its own on record keep that license and are kept in a folder of their own. Where no reuse license is on record for a source, a description taken from it is not reissued and the source is named instead; the names of value options are listed, each with its source.
- `other_licenses/fungaltraits/` holds 16 characters and 260 value options whose words are another source's: Põlme S. et al. 2020. FungalTraits: a user-friendly traits database of fungi and fungus-like stramenopiles. Fungal Diversity 105: 1-16. doi:10.1007/s13225-020-00466-2. Table S1, Traits of genera. License: CC BY-NC, as a university repository lists the supplementary table; publisher copyright 2021 Mushroom Research Foundation. The license was not confirmed with the authors. The words are the authors'. They are shown as written and are not corrected here; a correction is theirs to make.
- 160 value options have a description on record that was taken from a book or a website for which no reuse
  license is on record. The description is not in this release. `value_options.csv` names its source.
- The name of a value option is listed with the source the list took it from. 331 names
  come from a book or a website for which no reuse license is on record. Most are a single term of the field, such as a word
  for a shape; 34 are longer: a term with a few words of explanation, or a short phrase, like
  "Farinaceous (like fresh meal)".

## Consumption
No advice about consumption. MRDBID records how sources describe fungi. It is not a guide to eating, using or handling any fungus, and nothing here says whether any fungus is safe. Values about chemistry or toxicity are reported only as their source states them.

## The files
- `parts.csv`, `characters.csv`, `value_options.csv` — the open list. Each row: the identifier, the name shown and
  the name as written; a character and a value option also say where they came from. A character carries its
  English and its Latin name; where they are the same the word has one form. The two names are display forms and are not in the lists of changes: 42
  Latin names differ from the name in the list in the form of a word (lamellae for lamella), in showing one of two
  words the list wrote side by side (context for "context flesh"), or in the scientific word for a plain one (stipe
  for stem).
  `xde_item` is the number of the item of the first list that the character was parsed from or matches. The
  sentences of that list are not carried in this release.
- `vocabulary.json` — the same list in one file, with the names tagged en-US and la.
- `keys.csv` — the key of every part, character and value option in the MRDBID database, with its identifier.
  683 character keys and 757 value option keys; a name joined into another character
  carries that character's identifier.
- `changes/spelling_corrections.csv` — 138 corrections of spelling inside a name as stored: letters, capital
  letters, hyphens and other marks, spaces. Nothing else about the name changes in this list.
- `changes/new_versions_and_links.csv` — 676 changes that are more than spelling: words removed or added, names joined,
  value options added, a unit or a type set. Each names its basis. `name_as_stored` is the name in the MRDBID
  database; `from` and `to` are the change itself, which may start from a name already changed by another row.
- `left_for_users.csv` — what no source decides. It is shown as written and left for the people who use the list.
- `sources.csv` — every source used, with its license or what is known of it.
- `other_licenses/fungaltraits/` — the words of another source, under that source's license.
- `MANIFEST.json` — the counts and a checksum of every file.

## Credits
The first list: "Observation List: Characters With Taxonomic Value For Stipitate-Lamellate Mushrooms", Mushroom Observer species list 1417. Most of the characters were parsed from it. In these files "XDE" is the
short tag of that list. Its author gave Will Johnston his blessing to use the list and asked for no credit; he was content to have the list itself credited. He names the work his list rests on: the literature of Dr. Gastón Guzmán, correspondence with Alan Rockefeller, and the literature of Else Vellinga, whose glossary in Flora Agaricina Neerlandica he recommends to others.
Compiled by Will Johnston. Built with Claude (Anthropic).
