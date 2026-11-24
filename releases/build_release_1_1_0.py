#!/usr/bin/env python3
"""Build release 1.1.0 of the Mushroom Character Vocabulary: release 1.0.0 as published, plus step 2.

Add-only. Release 1.0.0 is read, never changed. What 1.1.0 adds:
  - definitions.csv  the definition records of step 2 (parts, characters, value options) and of the additions
  - units.csv        the unit of each measurement character, with its UO identifier
  - links.csv        'same as', 'close' and 'not the same' links; nothing merged
  - references.csv   the references of the shared register that bear on the vocabulary, with the identifiers
                     of the characters a reference is cited for
  - the additions of step 2 (definitions/additions.csv): one character, its four value options, 72 value
    options, 14 units where 1.0.0 had none, 2 units as new versions (mm to µm for spore ranges)
  - the disclaimer of shared_reference/disclaimer/ at the top and bottom of README.md
The register, releases/identifiers.csv, gets the next numbers for the additions (first_release 1.1.0).
Run from anywhere: python3 releases/build_release_1_1_0.py
MIT License.
"""
import collections, csv, datetime, hashlib, io, json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))              # Character_Vocabulary/releases
PROJ = os.path.dirname(HERE)                                   # Character_Vocabulary
SHARED = os.path.join(os.path.dirname(PROJ), "shared_reference")
BASE_V, V = "1.0.0", "1.1.0"
PREPARED = "2026-11-24"
SRC = os.path.join(HERE, BASE_V)
OUT = os.path.join(HERE, V)
DEF = os.path.join(PROJ, "definitions")
RUNS = {"parts": "parts_2026-11-23", "values": "values_all_parts_2026-11-23",
        "characters": "characters_2026-11-23", "units": "units_2026-11-23", "links": "links_2026-11-23"}
REG = os.path.join(HERE, "identifiers.csv")
GREEK = (("α", "alpha"), ("β", "beta"), ("γ", "gamma"), ("δ", "delta"), ("ε", "epsilon"))
KAUFFMAN = "KAUFFMAN1918"
KAUFFMAN_LIC = "public domain in the United States (published 1918)"
KAUFFMAN_TITLE = ("Kauffman, C. H. 1918. The Agaricaceae of Michigan, vol. 1. Michigan Geological and Biological "
                  "Survey Publication 26, Biological Series 5. Glossary, pp. 879-899")
ADDED = "added in 1.1.0"

# References of the shared register that bear on the vocabulary: the sections, and the rows of 'Added since'
# that are about characters, words or sources of the list. The rules of Alabama's collecting review are
# not about characters and stay in the shared register (shown on the sites), not in this release.
REF_SECTIONS_ALL = ("Will's original list", "Cited in XDE's list")
REF_ADDED_SINCE = {"REF-0043", "REF-0044", "REF-0045", "REF-0048", "REF-0049", "REF-0050", "REF-0051", "REF-0052",
                   "REF-0053", "REF-0054", "REF-0055", "REF-0056", "REF-0057", "REF-0058", "REF-0059", "REF-0060",
                   "REF-0061", "REF-0062", "REF-0063", "REF-0064", "REF-0065", "REF-0075", "REF-0077", "REF-0079"}
# The characters a reference of XDE's list is cited for: the URL found in the sentence of that item
# (rebuild/.../xde_match.csv), the character key mapped through keys.csv of release 1.0.0. Item 125 is a link
# to a video with no character of its own; it follows item 124, whose character it is listed under.
XDE_MATCH = os.path.join(PROJ, "rebuild", "character_list_2026-11-19_120047", "xde_match.csv")
XDE_URL_TOKENS = {"REF-0121": "show_species_list/1770", "REF-0122": "show_species_list/2051",
                  "REF-0123": "glossary_terms/1856", "REF-0124": "show_species_list/2012",
                  "REF-0125": "glossary_terms/1073", "REF-0126": "mushroomobserver.org/460796",
                  "REF-0127": "show_species_list/2042", "REF-0128": "mushroomobserver.org/487056",
                  "REF-0129": "show_species_list/2040", "REF-0130": "M9joL8spvS8",
                  "REF-0131": "show_species_list/401", "REF-0132": "glossary_terms/2303",
                  "REF-0133": "glossary_terms/1956", "REF-0134": "glossary_terms/1529",
                  "REF-0135": "chemrxiv.org", "REF-0136": "Andersson et al., 2008"}
XDE_NO_CHARACTER = {"REF-0130": ("124", "item 125 is a link to a video with no character of its own; it follows item 124")}


def stop(msg):
    sys.exit("STOPPED: " + msg)


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, fields, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in fields})
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def letters(s):
    for g, n in GREEK:
        s = s.replace(g, n)
    return re.sub(r"[^a-z0-9]+", "", s.casefold())


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def fields_of(path):
    with open(path, newline="", encoding="utf-8") as f:
        return next(csv.reader(f))


def main():
    if os.path.exists(OUT):
        stop(f"{OUT} exists. A release folder is built once; move it aside to build again.")
    disc = json.load(open(os.path.join(SHARED, "disclaimer", "disclaimer.json"), encoding="utf-8"))
    full = disc["full"].replace("This site", "This vocabulary")
    lead, near = disc["lead"], disc["near_item"]
    if not full.startswith("This vocabulary") or lead != "No advice about consumption.":
        stop("the disclaimer's wording is not as expected")

    parts = read(os.path.join(SRC, "parts.csv"))
    chars = read(os.path.join(SRC, "characters.csv"))
    vos = read(os.path.join(SRC, "value_options.csv"))
    c_fields = fields_of(os.path.join(SRC, "characters.csv"))
    v_fields = fields_of(os.path.join(SRC, "value_options.csv"))
    by_cid = {c["id"]: c for c in chars}
    reg = read(REG)
    reg_by_key = {r["key"]: r for r in reg}
    reg_by_id = {r["id"]: r for r in reg}
    if len(reg) < 2167 or any(r["first_release"] not in (BASE_V, V) for r in reg):
        stop("the register is not release 1.0.0's register (plus this build's own rows)")
    next_no = max(int(r["id"][4:]) for r in reg) + 1
    new_reg = []

    def give(kind, key):
        nonlocal next_no
        if key in reg_by_key:
            r = reg_by_key[key]
            if r["kind"] != kind:
                stop(f"register key {key} is a {r['kind']}, not a {kind}")
            return r["id"]
        i = "MCV_%07d" % next_no
        next_no += 1
        row = {"id": i, "kind": kind, "key": key, "first_release": V, "status": "proposed", "replaced_by": ""}
        reg.append(row); reg_by_key[key] = row; reg_by_id[i] = row; new_reg.append(row)
        return i

    def char_row_key(cid):  # 'character:120' -> '120'; 'character:NEW-2' -> 'NEW-2'
        k = reg_by_id[cid]["key"]
        if not k.startswith("character:"):
            stop(f"{cid} is not a character in the register")
        return k.split(":", 1)[1]

    # ---- 1 the additions
    adds = read(os.path.join(DEF, "additions.csv"))
    changes, new_chars, new_vos, add_defs = [], [], [], []
    unit_change = {}
    label_id = {}  # NEW-Dn of an added value option -> its new identifier (the values run holds its record)
    existing_vo = collections.defaultdict(set)
    for v in vos:
        existing_vo[v["character_id"]].add(letters(v["value_option_name"]))

    for a in adds:
        lab, kind = a["label"], a["kind"]
        if kind == "character":
            proto = by_cid["MCV_0000241"]  # universal veil present: same part, group, kind, type, value options
            cid = give("character", "character:" + lab)
            row = dict(proto)
            row.update({"id": cid, "character_name_english": a["name_english"],
                        "character_name_latin": a["name_english"], "character_name_as_written": a["name_english"],
                        "also_written_as": "", "part_id": a["part_id"], "in_this_release": ADDED,
                        "xde_item": "", "pubchem_cid": "", "inchikey": "", "chebi": "", "note": "",
                        "values_recorded": "0", "origin": KAUFFMAN_TITLE + " (step 2 of this vocabulary)",
                        "mrdbid_character_keys": ""})
            new_chars.append(row)
            by_cid[cid] = row
            changes.append({"label": lab, "id": cid, "kind": "character added", "from": "",
                            "to": a["name_english"], "basis": a["evidence"] + ". " + a["reason"]})
            pv = [d for d in read(os.path.join(DEF, RUNS["parts"], "definitions.csv"))
                  if d["source"] == KAUFFMAN and d["source_headword"] == "PARTIAL VEIL"]
            if len(pv) != 1 or pv[0]["page"] != "892":
                stop(f"{lab}: the verified PARTIAL VEIL record of the parts run is not found once")
            add_defs.append({"target_id": cid, "target_kind": "character", "relation": "the structure it describes",
                             "source": KAUFFMAN, "source_headword": "PARTIAL VEIL", "page": "892",
                             "text": pv[0]["text"], "license": KAUFFMAN_LIC, "checked": pv[0]["checked"],
                             "note": f"The entry that gave the addition {lab}; the same as record {pv[0]['record']}."})
            for name in a["value_options"].split("|"):
                vid = give("value option", f"value_option:{lab}:{letters(name)}")
                new_vos.append({"id": vid, "character_id": cid, "value_option_name": name,
                                "value_option_as_written": name, "status": "proposed",
                                "in_this_release": ADDED + ": one of Yes, No, Unknown, Not Tested",
                                "description_on_record": "", "description_source": "",
                                "origin": "the general list of this vocabulary", "values_recorded": "0",
                                "mrdbid_value_option_keys": ""})
        elif kind == "value option":
            cid = a["character_id"]
            if cid not in by_cid:
                stop(f"{lab}: character {cid} is not in release 1.0.0")
            if letters(a["name_english"]) in existing_vo[cid]:
                stop(f"{lab}: {a['name_english']} is already a value option of {cid}")
            existing_vo[cid].add(letters(a["name_english"]))
            vid = give("value option", f"value_option:{char_row_key(cid)}:{letters(a['name_english'])}")
            new_vos.append({"id": vid, "character_id": cid, "value_option_name": a["name_english"],
                            "value_option_as_written": a["name_english"], "status": "proposed",
                            "in_this_release": ADDED + " from Kauffman 1918",
                            "description_on_record": "", "description_source": "",
                            "origin": KAUFFMAN_TITLE, "values_recorded": "0", "mrdbid_value_option_keys": ""})
            changes.append({"label": lab, "id": vid, "kind": "value option added", "from": "",
                            "to": a["name_english"], "basis": a["evidence"] + " " + a["reason"]})
            label_id[lab] = vid
        elif kind in ("unit", "unit (new version)"):
            cid = a["character_id"]
            c = by_cid[cid]
            if kind == "unit" and c["unit"]:
                stop(f"{lab}: {cid} already has unit {c['unit']}")
            if kind == "unit (new version)" and c["unit"] != "mm":
                stop(f"{lab}: {cid} has unit {c['unit']!r}, not mm")
            unit_change[cid] = (c["unit"], a["name_english"], lab, a["reason"])
            changes.append({"label": lab, "id": cid,
                            "kind": "unit set" if kind == "unit" else "unit: new version",
                            "from": c["unit"], "to": a["name_english"], "basis": a["reason"]})
        else:
            stop(f"{lab}: unknown kind {kind}")

    out_chars = []
    for c in chars:
        c = dict(c)
        if c["id"] in unit_change:
            old, new = unit_change[c["id"]][:2]
            c["unit"] = new
            c["in_this_release"] += ("; unit set in 1.1.0" if not old else f"; unit: new version in 1.1.0 ({BASE_V}: {old})")
        out_chars.append(c)
    out_chars += new_chars
    out_vos = [dict(v) for v in vos] + new_vos

    # ---- 2 units, with UO identifiers (all measurement characters)
    units = read(os.path.join(DEF, RUNS["units"], "character_units.csv"))
    u_by = {u["target_id"]: u for u in units}
    for cid, (old, new, lab, _) in unit_change.items():
        u = u_by.get(cid)
        if not u or u["unit"] != new:
            stop(f"{lab}: the units run gives {u and u['unit']!r} for {cid}, the addition {new!r}")
    for c in out_chars:
        if c["type"] == "numeric" and c["id"] not in u_by:
            stop(f"numeric character {c['id']} has no row in the units run")
        if c["id"] in u_by and c["unit"] != u_by[c["id"]]["unit"]:
            stop(f"{c['id']}: unit {c['unit']!r} in the release, {u_by[c['id']]['unit']!r} in the units run")
    unit_rows = [{"character_id": u["target_id"], "character_name_english": u["character_name_english"],
                  "unit": u["unit"], "unit_name_english": u["unit_name_english"], "uo_id": u["uo_id"],
                  "uo_name": u["uo_name"],
                  "in_this_release": "as in 1.0.0" if u["target_id"] not in unit_change else
                  ("set in 1.1.0" if not unit_change[u["target_id"]][0] else "new version in 1.1.0 (1.0.0: mm)"),
                  "note": u["note"]} for u in units]

    # ---- 3 definitions: the three runs plus the additions, every record with a source
    D_FIELDS = ["record", "target_id", "target_kind", "target_name", "relation", "source", "source_id",
                "source_headword", "page", "text", "license", "checked", "part_definition_records", "note"]
    defs, absent = [], collections.Counter()
    names = {p["id"]: p["part_name_english"] for p in parts}
    names.update({c["id"]: c["character_name_english"] for c in out_chars})
    names.update({v["id"]: v["value_option_name"] for v in out_vos})
    for run, kind in (("parts", "part"), ("characters", "character"), ("values", "value option")):
        for r in read(os.path.join(DEF, RUNS[run], "definitions.csv")):
            if r["target_id"].startswith("NEW-D"):
                if r["target_id"] not in label_id:
                    stop(f"{r['record']}: {r['target_id']} is not an added value option")
                r["target_id"] = label_id.pop(r["target_id"])
            if r["target_id"] not in names:
                stop(f"{r['record']}: {r['target_id']} is not in the release")
            if r["relation"] == "none":
                absent[kind] += 1
                continue
            if r["source"] == KAUFFMAN and (not r["text"] or r["license"] != KAUFFMAN_LIC):
                stop(f"{r['record']}: a Kauffman record without its text or license")
            if r["source"] == "FAO" and r["text"]:
                stop(f"{r['record']}: FAO wording would be carried")
            if r["source"] == "PubChem" and r["text"]:
                stop(f"{r['record']}: PubChem wording would be carried")
            if r["source_headword"] == "MYCELIUM" and r["text"].startswith("came as hyphae") and not r["note"]:
                r["note"] = "'came' is as printed; evidently 'same'."
            defs.append({"record": r["record"], "target_id": r["target_id"], "target_kind": kind,
                         "target_name": names[r["target_id"]], "relation": r["relation"], "source": r["source"],
                         "source_id": r.get("source_term_id") or r.get("source_id", ""),
                         "source_headword": r["source_headword"], "page": r["page"], "text": r["text"],
                         "license": r["license"], "checked": r["checked"],
                         "part_definition_records": r.get("part_definition_records", ""), "note": r["note"]})
    if label_id:
        stop(f"added value options with no definition record: {sorted(label_id)}")
    for n, r in enumerate(add_defs, 1):
        r = dict(r)
        r["record"] = "A%05d" % n
        r["target_name"] = names[r["target_id"]]
        defs.append(r)
    ANSWER = {"yes", "no", "unknown", "nottested", "other", "none"}
    with_rec = {d["target_id"] for d in defs}
    searched_none = {r["target_id"] for r in read(os.path.join(DEF, RUNS["values"], "definitions.csv"))
                     if r["relation"] == "none"}
    vo_cov = collections.Counter()
    for v in out_vos:
        if v["id"] in with_rec:
            vo_cov["with a record"] += 1
        elif v["id"] in searched_none:
            vo_cov["searched, no entry found"] += 1
        elif letters(v["value_option_name"]) in ANSWER:
            vo_cov["answer words, not looked up"] += 1
        else:
            vo_cov["not searched"] += 1
    if sum(vo_cov.values()) != len(out_vos) or vo_cov["searched, no entry found"] != absent["value option"]:
        stop("value option coverage does not add up")
    recs = [d["record"] for d in defs]
    if len(recs) != len(set(recs)):
        stop("two definition records share a number")

    # ---- 4 links
    links = read(os.path.join(DEF, RUNS["links"], "links.csv"))
    for l in links:
        for k in ("from_id", "to_id"):
            if l[k] not in names:
                stop(f"{l['link']}: {l[k]} is not in the release")
    l_fields = list(links[0].keys())

    # ---- 5 references
    refs = read(os.path.join(SHARED, "references", "references.csv"))
    xm = read(XDE_MATCH)
    k_char = {k["mrdbid_key"]: k["id"] for k in read(os.path.join(SRC, "keys.csv")) if k["record"] == "character"}
    out_refs = []
    for r in refs:
        sec = r["section"]
        if not (sec.startswith(REF_SECTIONS_ALL) or r["ref_id"] in REF_ADDED_SINCE):
            continue
        if r["display"] != "yes":
            continue
        ids, how = [], ""
        if r["ref_id"] in XDE_URL_TOKENS:
            tok = XDE_URL_TOKENS[r["ref_id"]]
            hits = [x for x in xm if tok in x["xde_sentence"]]
            if not hits:
                stop(f"{r['ref_id']}: its address is in no sentence of XDE's list")
            items = sorted({x["xde_item"] for x in hits}, key=int)
            for x in hits:
                if x["character_key"]:
                    ids.append(k_char[x["character_key"]])
            if r["ref_id"] in XDE_NO_CHARACTER:
                item, why = XDE_NO_CHARACTER[r["ref_id"]]
                ids += [c["id"] for c in chars if item in c["xde_item"].split()]
                how = why
            if not ids:
                stop(f"{r['ref_id']}: no character found")
            how = (f"cited in XDE's list, item {', '.join(items)}" + ("; " + how if how else ""))
        out_refs.append({"ref_id": r["ref_id"], "section": sec, "title": r["title"], "authors": r["authors"],
                         "edition_year": r["edition_year"], "kind": r["kind"], "identifier": r["identifier"],
                         "license": r["license"], "use": r["use"], "cited_for_ids": " ".join(sorted(set(ids))),
                         "cited_how": how,
                         "consumption_notice": r["consumption_notice"],
                         "notice": (lead + " " + near) if r["consumption_notice"] == "yes" else ""})

    # ---- 6 sources: 1.0.0's rows plus those step 2 added
    sources = read(os.path.join(SRC, "sources.csv"))
    s_fields = fields_of(os.path.join(SRC, "sources.csv"))
    sources += [
        {"source": KAUFFMAN_TITLE, "license": KAUFFMAN_LIC + "; scan of the New York Botanical Garden copy, "
         "Internet Archive item agaricaceaeofmic01kauf, marked not in copyright", "read": "2026-11-23",
         "used_for": "definitions quoted word for word in definitions.csv, each read from the page image"},
        {"source": "Units of Measurement Ontology (UO), release 2026-10-12, http://purl.obolibrary.org/obo/uo.owl",
         "license": "CC BY 4.0, as its file states; credited in other_licenses/uo/; identifiers and names only",
         "read": "2026-11-23", "used_for": "the identifier and name of each unit in units.csv"},
        {"source": "UCUM, Unified Code for Units of Measure, license version 1.1 (June 2024), Regenstrief Institute",
         "license": "read only; not used (revocable license, no derivative works)", "read": "2026-11-23",
         "used_for": "the choice of unit standard (UO chosen)"},
        {"source": "References register of Will Johnston's projects (shared_reference/references/references.csv)",
         "license": "CC0 1.0 for the register itself; each reference keeps its own license",
         "read": PREPARED, "used_for": "references.csv"},
    ]
    for s in sources:
        if s["source"].startswith("PubChem") and "definitions.csv" not in s["used_for"]:
            s["used_for"] += "; in 1.1.0 also the pointer records of definitions.csv (identifiers only)"
        if s["source"].startswith('Fungal Anatomy Ontology') and "definitions.csv" not in s["used_for"]:
            s["used_for"] += "; in 1.1.0 also the pointer records of definitions.csv (identifiers and term names, no FAO wording)"

    # ---- 7 write the folder
    os.makedirs(OUT)
    write_csv(os.path.join(OUT, "parts.csv"), fields_of(os.path.join(SRC, "parts.csv")), parts)
    write_csv(os.path.join(OUT, "characters.csv"), c_fields, out_chars)
    write_csv(os.path.join(OUT, "value_options.csv"), v_fields, out_vos)
    for f in ("keys.csv", "left_for_users.csv"):
        shutil.copy2(os.path.join(SRC, f), os.path.join(OUT, f))
    shutil.copytree(os.path.join(SRC, "changes"), os.path.join(OUT, "changes"))
    shutil.copytree(os.path.join(SRC, "other_licenses"), os.path.join(OUT, "other_licenses"))
    write_csv(os.path.join(OUT, "changes", "changes_in_1.1.0.csv"),
              ["label", "id", "kind", "from", "to", "basis"], changes)
    write_csv(os.path.join(OUT, "definitions.csv"), D_FIELDS, defs)
    write_csv(os.path.join(OUT, "units.csv"), list(unit_rows[0].keys()), unit_rows)
    write_csv(os.path.join(OUT, "links.csv"), l_fields, links)
    write_csv(os.path.join(OUT, "references.csv"), list(out_refs[0].keys()), out_refs)
    write_csv(os.path.join(OUT, "sources.csv"), s_fields, sources)
    write_text(os.path.join(OUT, "other_licenses", "uo", "README.md"),
               "# Units of Measurement Ontology (UO)\n\n`units.csv` carries, for each unit, the UO identifier "
               "(such as UO:0000016) and the UO name of the unit (such as millimeter). They are taken from UO, "
               "release 2026-10-12, http://purl.obolibrary.org/obo/uo.owl, which is licensed CC BY 4.0 "
               "(https://creativecommons.org/licenses/by/4.0/). Credit: Unit Ontology, Gkoutos G. V., Schofield "
               "P. N., Hoehndorf R. et al., https://github.com/bio-ontology-research-group/unit-ontology. "
               "No other UO wording is carried. The rest of the release is CC0 1.0.\n")

    # vocabulary.json: 1.0.0's file, carried forward with the additions and step 2
    voc = json.load(open(os.path.join(SRC, "vocabulary.json"), encoding="utf-8"))
    voc["version"], voc["prepared"] = V, PREPARED
    voc["consumption"] = lead + " " + full
    voc["license"] = ("CC0 1.0 Universal, except the UO identifiers and unit names (unit_uo, CC BY 4.0, Units of "
                      "Measurement Ontology; see other_licenses/uo/) and the entries under other_licenses/")
    d_by_target = collections.defaultdict(list)
    for d in defs:
        d_by_target[d["target_id"]].append(d["record"])
    for c in voc["characters"]:
        if c["id"] in unit_change:
            c["unit"] = unit_change[c["id"]][1]
        if c["id"] in u_by:
            c["unit_uo"] = u_by[c["id"]]["uo_id"]
        c["definitions"] = d_by_target.get(c["id"], [])
        for v in c["value_options"]:
            v["definitions"] = d_by_target.get(v["id"], [])
    for p in voc["parts"]:
        p["definitions"] = d_by_target.get(p["id"], [])
    vo_by_char = collections.defaultdict(list)
    for v in new_vos:
        vo_by_char[v["character_id"]].append(v)
    cv = {c["id"]: c for c in voc["characters"]}
    for cid, vs in vo_by_char.items():
        if cid not in cv:
            continue
        for v in vs:
            cv[cid]["value_options"].append({"id": v["id"], "label": v["value_option_name"],
                                             "as_written": v["value_option_as_written"], "status": "proposed",
                                             "definitions": d_by_target.get(v["id"], [])})
    for c in new_chars:
        voc["characters"].append({"id": c["id"], "labels": {"en-US": c["character_name_english"],
                                                            "la": c["character_name_latin"]},
                                  "as_written": [c["character_name_as_written"]], "part": c["part_id"],
                                  "group": c["group"], "kind": c["kind"], "type": c["type"], "unit": c["unit"],
                                  "status": "proposed", "pubchem_cid": "", "inchikey": "", "chebi": "",
                                  "definitions": d_by_target.get(c["id"], []),
                                  "value_options": [{"id": v["id"], "label": v["value_option_name"],
                                                     "as_written": v["value_option_as_written"],
                                                     "status": "proposed", "definitions": []}
                                                    for v in vo_by_char[c["id"]]]})
    voc["definitions"] = defs
    voc["links"] = links
    voc["references"] = out_refs
    with open(os.path.join(OUT, "vocabulary.json"), "w", encoding="utf-8") as f:
        json.dump(voc, f, ensure_ascii=False, indent=1)
        f.write("\n")

    # the register (add-only)
    reg_fields = fields_of(REG)
    if new_reg:
        with open(REG, "a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=reg_fields, lineterminator="\n")
            for r in new_reg:
                w.writerow(r)

    # ---- 8 counts, README, LICENSE, MANIFEST
    rel_counts = collections.Counter((d["target_kind"], d["relation"]) for d in defs)
    src_counts = collections.Counter(d["source"] for d in defs)
    n_ft_c = len(read(os.path.join(SRC, "other_licenses", "fungaltraits", "characters.csv")))
    n_ft_v = len(read(os.path.join(SRC, "other_licenses", "fungaltraits", "value_options.csv")))
    regall = read(REG)
    counts = {
        "identifiers": len(regall), "identifiers_new_in_1.1.0": len([r for r in regall if r["first_release"] == V]),
        "parts": len(parts), "characters": len(out_chars) + n_ft_c, "characters_cc0": len(out_chars),
        "characters_other_license": n_ft_c, "value_options": len(out_vos) + n_ft_v,
        "value_options_cc0": len(out_vos), "value_options_other_license": n_ft_v,
        "characters_added": len(new_chars), "value_options_added": len(new_vos),
        "units": len(unit_rows), "units_set_in_1.1.0": sum(1 for v in unit_change.values() if not v[0]),
        "units_new_version_in_1.1.0": sum(1 for v in unit_change.values() if v[0]),
        "definition_records": len(defs), "definition_records_by_source": dict(src_counts),
        "definition_records_by_target_and_relation": {f"{k[0]}: {k[1]}": n for k, n in sorted(rel_counts.items())},
        "parts_with_no_source_found": absent["part"], "characters_with_no_source_found": absent["character"],
        "value_options_by_definition": dict(vo_cov),
        "links": len(links), "links_by_kind": dict(collections.Counter(f"{l['kind']}: {l['relation']}" for l in links)),
        "references": len(out_refs), "references_with_notice": sum(1 for r in out_refs if r["notice"]),
        "references_cited_for_characters": sum(1 for r in out_refs if r["cited_for_ids"]),
    }
    if counts["identifiers"] != 2167 + counts["identifiers_new_in_1.1.0"]:
        stop("identifier count does not add up")

    disc_block = f"> **{lead}** {full}\n"
    rc = counts["definition_records_by_target_and_relation"]
    def rcount(prefix):
        return "; ".join(f"{k.split(': ',1)[1]} {n}" for k, n in rc.items() if k.startswith(prefix + ":"))
    readme = f"""{disc_block}
# Mushroom Character Vocabulary, release {V}

Prepared {PREPARED}. A proposal for use. Nobody can declare a standard; adoption comes from use. Every part, character and value option is marked proposed.

Will Johnston, 2026-11-14: "The goal is to improve the accuracy of fungi data by providing tools to citizen scientists and others that make this goal easier."

## What is new in {V}
Release {BASE_V} is unchanged and stays as published; this release is {BASE_V} plus what step 2 added. Nothing was removed and no identifier changed.
- **Definitions** (`definitions.csv`): {counts['definition_records']} sourced records. Each names the entry it is for, the relation, the source, the page and, where the source's license allows it, the exact words.
  - Parts: {rcount('part')}.
  - Characters: {rcount('character')}.
  - Value options: {rcount('value option')}.
  - Wording is quoted only from Kauffman 1918 (public domain in the United States), each quotation read from the page image. The Fungal Anatomy Ontology (FAO) and PubChem are pointers: an identifier and a name, no wording.
  - Entries with no record: {absent['part']} parts and {absent['character']} characters for which no source was found. Of the {len(out_vos)} value options in the open list, {vo_cov['with a record']} have a record; {vo_cov['searched, no entry found']} were searched and no entry was found; {vo_cov['answer words, not looked up']} are answer words (Yes, No, Unknown, Not Tested, Other, None), not defined as words; {vo_cov['not searched']} were not searched in step 2.
  - An old wording is a record of how a source used a word, not a statement of current science. A printing error is quoted as printed and named in the record's note.
- **Units** (`units.csv`): the unit of each of the {counts['units']} measurement characters with its identifier in the Units of Measurement Ontology (UO). {counts['units_set_in_1.1.0']} units set where {BASE_V} had none; {counts['units_new_version_in_1.1.0']} spore-range units given as µm in place of mm, as new versions.
- **Links** (`links.csv`): {counts['links']} links between characters and between value options: 'same as', 'close' and 'not the same'. Nothing is merged; both ends stay in the list.
- **Additions**: {counts['characters_added']} character (partial veil present, with the four value options Yes, No, Unknown, Not Tested) and {counts['value_options_added'] - 4} value options from Kauffman's glossary, each with its evidence in `changes/changes_in_1.1.0.csv`. {counts['identifiers_new_in_1.1.0']} new identifiers, {regall[2167]['id']} to {regall[-1]['id']}.
- **References** (`references.csv`): {counts['references']} references, the ones of the shared references register that bear on this vocabulary. {counts['references_cited_for_characters']} name the characters they are cited for. {counts['references_with_notice']} carry the notice "{lead}" beside them because their subject includes eating or using fungi; they are listed for how they describe fungi.

| | |
|---|---|
| Identifiers | {counts['identifiers']} (MCV_0000001 to {regall[-1]['id']}) |
| Parts | {counts['parts']} |
| Characters | {counts['characters']} ({counts['characters_cc0']} in the open list, {n_ft_c} under another source's license) |
| Value options | {counts['value_options']} ({counts['value_options_cc0']} in the open list, {n_ft_v} under another source's license) |
| Definition records | {counts['definition_records']} |
| Units | {counts['units']} |
| Links | {counts['links']} |
| References | {counts['references']} |

## The identifiers
MCV_ and seven digits. The number means nothing: it is only the order in which an identifier was given. Written in full: https://w3id.org/mcv/MCV_0000001.
- An identifier is given once and never reused. It is never deleted: a retired one stays in the register with a pointer to what replaced it.
- The wording may change from release to release; the identifier does not.
- The register, identifiers.csv, is add-only. Each row says the release that first gave the identifier.

## License
CC0 1.0 Universal for the files of the open list, as in {BASE_V}, except the UO identifiers and unit names (CC BY 4.0); see LICENSE.md.
- The quotations in `definitions.csv` are from Kauffman 1918, public domain in the United States.
- The UO identifiers and unit names in `units.csv` are from UO, CC BY 4.0, credited in `other_licenses/uo/`.
- `other_licenses/fungaltraits/` is unchanged from {BASE_V}: its words keep their authors' license.
- `references.csv` lists works by title. A title is cited, not copied; each work keeps its own license.

## The files
- `parts.csv`, `characters.csv`, `value_options.csv` — the open list, as in {BASE_V}, with the additions and the units of this release.
- `definitions.csv` — the definition records. `relation` says what the record is to its entry: for a value option, `defines` (the source's entry for that word and that part), `related` (an entry for the word for another part), `cross-reference`; for a character, `the structure it describes`, `the quality it records`, `the term it records`, `related`, `cross-reference`, `pointer` (PubChem); for a part, `defines`, `narrower`, `cross-reference`, `describes the group`. `part_definition_records` gives, for a character, the records of its part.
- `units.csv` — unit, UO identifier and UO name of each measurement character.
- `links.csv` — the links, each with its basis.
- `references.csv` — the references, with `cited_for_ids` and the notice where it applies.
- `changes/changes_in_1.1.0.csv` — every addition and unit change of this release, with its evidence. The two files of {BASE_V} are carried unchanged.
- `vocabulary.json` — the same list in one file, with definitions, units, links and references.
- `keys.csv`, `left_for_users.csv`, `sources.csv`, `other_licenses/` — as in {BASE_V}; `sources.csv` adds the sources of step 2.
- `MANIFEST.json` — the counts and a checksum of every file.

## Credits
The first list: "Observation List: Characters With Taxonomic Value For Stipitate-Lamellate Mushrooms", Mushroom Observer species list 1417, used by its author's permission (see {BASE_V}). Definitions: C. H. Kauffman, The Agaricaceae of Michigan (1918), scan of the New York Botanical Garden copy at the Internet Archive. Units: the Units of Measurement Ontology. Compiled by Will Johnston. Built with Claude (Anthropic).

{disc_block}"""
    write_text(os.path.join(OUT, "README.md"), readme)
    lic = open(os.path.join(SRC, "LICENSE.md"), encoding="utf-8").read()
    lic = lic.replace(f"release {BASE_V}", f"release {V}")
    lic = lic.replace("the two files under changes/", "the files under changes/")
    if "value_options.csv, vocabulary.json, keys.csv" not in lic:
        stop("the waiver sentence of LICENSE.md is not as expected")
    lic = lic.replace("value_options.csv, vocabulary.json, keys.csv",
                      "value_options.csv, vocabulary.json (except its UO identifiers and names), keys.csv")
    lic = lic.replace("left_for_users.csv, sources.csv, and",
                      "left_for_users.csv, sources.csv, definitions.csv, units.csv (except its UO identifiers and "
                      "UO names, which are CC BY 4.0; see other_licenses/uo/), links.csv, references.csv, "
                      "and")
    lic += ("\nIn release 1.1.0: the quotations in definitions.csv are from Kauffman 1918, which is in the public "
            "domain in the United States. The UO identifiers and unit names in units.csv are from the Units of "
            "Measurement Ontology, CC BY 4.0, credited in `other_licenses/uo/`. FAO and PubChem are cited by "
            "identifier and name only. references.csv cites works by title; each work keeps its own license.\n\n"
            f"**{lead}** {full}\n")
    write_text(os.path.join(OUT, "LICENSE.md"), lic)
    files = sorted(os.path.relpath(os.path.join(d, f), OUT) for d, _, fs in os.walk(OUT) for f in fs)
    manifest = {"what": f"Mushroom Character Vocabulary, release {V}: release {BASE_V} plus step 2 "
                        "(definitions, units, links, additions, references); a release candidate until published",
                "built_on": {"release": BASE_V, "manifest_sha256": sha(os.path.join(SRC, "MANIFEST.json"))},
                "inputs": {os.path.relpath(p, PROJ): sha(p) for p in
                           [os.path.join(DEF, "additions.csv"), XDE_MATCH] + [os.path.join(DEF, RUNS[k], f) for k, f in
                                          (("parts", "definitions.csv"), ("values", "definitions.csv"),
                                           ("characters", "definitions.csv"), ("units", "character_units.csv"),
                                           ("links", "links.csv"))]},
                "shared_inputs": {"references.csv": sha(os.path.join(SHARED, "references", "references.csv")),
                                  "disclaimer.json": sha(os.path.join(SHARED, "disclaimer", "disclaimer.json"))},
                "register": {"file": "releases/identifiers.csv", "sha256": sha(REG), "identifiers": len(regall)},
                "made_by": {"tool": "releases/build_release_1_1_0.py", "sha256": sha(os.path.abspath(__file__))},
                "run_at_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "counts": counts,
                "files": {f: {"bytes": os.path.getsize(os.path.join(OUT, f)), "sha256": sha(os.path.join(OUT, f))}
                          for f in files}}
    with open(os.path.join(OUT, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(json.dumps(counts, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
