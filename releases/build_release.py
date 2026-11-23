#!/usr/bin/env python3
"""Build a release of the Mushroom Character Vocabulary: permanent identifiers and the files that carry them.

usage: python3 releases/build_release.py          (from Claude_AI/Character_Vocabulary; standard library only)

Reads   releases/release_rules.json              what the release holds, the identifier form, the lines it carries
        releases/identifiers.csv                 the register of identifiers, add-only (made on the first run)
        rebuild/<export>/, terms/<export>/       the rebuilt list, the two display names, spelling, chemical names
        ../MRDBID/data/exports/<export>/         the checksummed export: the names as stored, parts, origins, use
Writes  releases/<version>/                      the release, and releases/identifiers.csv

An identifier is given once, in the order parts, characters, value options, and is kept on every later run.
Words taken from a source with its own license go to a folder of their own; a description taken from a source that
states no reuse license is not written out at all, only its source is named. Changes for the site are kept in two
lists: spelling corrections (letters, capitals, marks, spaces inside the name as stored) and everything else.
A release is written for a reader outside the workspace: the rules hold the public wording of a basis and of what is
left for users, and the script stops if a note that only the workspace can read is still in a text of the release.
It stops, and writes nothing, if a count does not add up. No network.
"""
import collections, csv, datetime, hashlib, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CV = os.path.dirname(HERE)
GREEK = (("α", "alpha"), ("β", "beta"), ("γ", "gamma"), ("δ", "delta"), ("ε", "epsilon"))


def stop(msg):
    sys.exit("STOPPED: " + msg)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path):
    with io.open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, columns, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def letters(s):
    for g, n in GREEK:
        s = s.replace(g, n)
    return re.sub(r"[^a-z0-9]+", "", s.casefold())


def one_space(s):
    return " ".join(s.split())


PUBLIC = []  # the rewordings of the rules, each [pattern, what replaces it, how often it was used]


def public(text):
    """a release names no path of the workspace it was made in and no note that only the workspace can read"""
    text = re.sub(r"\s*\((?:MRDBID|Claude_AI)/[^)]*\)", "", text or "")
    for rule in PUBLIC:
        text, n = rule[0].subn(rule[1], text)
        rule[2] += n
    return text


LEAKS = ((r"\bS\d\d\b", "a code of the review sheet"), (r"review sheet|question \d+|in the sheet\b", "a note about the review sheet"),
         (r"(?<!\d\d\d\d-\d\d-\d\d )(?<![\d:])\b\d{1,2}:\d\d\b", "a clock time without its date"), (r"\brows? \d", "a row number of a working file"),
         (r"listed for Will|\bP\d{1,2}\b", "a note for the review"))
RELEASE_FILES = {"parts.csv", "characters.csv", "value_options.csv", "keys.csv", "spelling_corrections.csv", "new_versions_and_links.csv", "left_for_users.csv",
                 "sources.csv", "identifiers.csv"}


def main():
    rules_path = os.path.join(HERE, "release_rules.json")
    rules = json.load(io.open(rules_path, encoding="utf-8"))
    name, version = rules["export"], rules["version"]
    PUBLIC[:] = [[re.compile(pat), new, 0] for pat, new in rules["public_bases"]]
    P = rules["identifiers"]["prefix"]
    R, T = os.path.join(CV, "rebuild", name), os.path.join(CV, "terms", name)
    E = os.path.join(os.path.dirname(CV), "MRDBID", "data", "exports", name)
    for d in (R, T, E):
        if not os.path.isdir(d):
            stop("folder not found: " + d)
    term_rules = json.load(io.open(os.path.join(CV, "terms", "term_rules.json"), encoding="utf-8"))
    chem_rules = json.load(io.open(os.path.join(CV, "terms", "chemical_rules.json"), encoding="utf-8"))
    tn = read_csv(os.path.join(T, "characters_two_names.csv"))
    rb = {r["row"]: r for r in read_csv(os.path.join(R, "characters_rebuilt.csv"))}
    vs = read_csv(os.path.join(T, "value_options_spelling.csv"))
    cn = {r["row"]: r for r in read_csv(os.path.join(T, "chemical_names.csv"))}
    sp = read_csv(os.path.join(T, "spelling.csv"))
    changes = read_csv(os.path.join(R, "changes.csv"))
    ex_c = {r["character_key"]: r for r in read_csv(os.path.join(E, "characters.csv"))}
    ex_v = {r["value_option_key"]: r for r in read_csv(os.path.join(E, "value_options.csv"))}
    ex_p = read_csv(os.path.join(E, "parts.csv"))
    ex_o = read_csv(os.path.join(E, "origins.csv"))
    if len(tn) != len(rb) or set(r["row"] for r in tn) != set(rb):
        stop("the two-names file and the rebuilt list do not hold the same rows")
    OL = rules["other_license_origin"]

    def other(row):  # a character whose words are another source's
        return rb[row]["origin_title"].startswith(OL["starts_with"])

    # ---- 1 the things that get an identifier, in a fixed order
    part_names = {p["part_name"]: p for p in ex_p}
    part_forms = {p["part_name"]: p for p in term_rules["parts"]}
    things = [("part", "part:" + p["part_key"]) for p in sorted(ex_p, key=lambda p: int(p["part_key"]))]
    things += [("character", "character:" + r["row"]) for r in tn]
    vkey = {}
    for i, v in enumerate(vs):
        keys = v["value_option_keys"].split()
        k = "value_option:" + (keys[0] if keys else v["row"] + ":" + letters(v["value_option_shown"]))
        vkey[i] = k
        things.append(("value option", k))
    if len(set(k for _, k in things)) != len(things):
        dup = [k for k, n in collections.Counter(k for _, k in things).items() if n > 1]
        stop("two things would share one key in the register: %s" % dup[:5])

    # ---- 2 the register: keep what is there, give the next number to what is new
    reg_path = os.path.join(HERE, "identifiers.csv")
    register = read_csv(reg_path) if os.path.exists(reg_path) else []
    again = rules["identifiers"].get("restarted_before_publication")
    if register and again and sha256(reg_path) == again["register_replaced_sha256"]:
        register = []  # the numbers of a candidate nobody had used, given afresh once; the rules say why
    by_key = {r["key"]: r for r in register}
    nxt = max([int(r["id"].split("_")[1]) for r in register] or [0]) + 1
    for kind, key in things:
        if key not in by_key:
            r = {"id": "%s_%07d" % (P, nxt), "kind": kind, "key": key, "first_release": version, "status": "proposed", "replaced_by": ""}
            register.append(r)
            by_key[key] = r
            nxt += 1
    if len(set(r["id"] for r in register)) != len(register):
        stop("an identifier would be given twice")
    ID = {k: r["id"] for k, r in by_key.items()}

    # ---- 3 parts
    parts = []
    for p in sorted(ex_p, key=lambda p: int(p["part_key"])):
        f = part_forms.get(p["part_name"])
        parts.append({"id": ID["part:" + p["part_key"]], "part_name_english": f["en"] if f else p["part_name"], "part_name_latin": f["la"] if f else p["part_name"],
                      "part_name_as_written": p["part_name"], "display_order": p["display_order"], "status": "proposed", "mrdbid_part_key": p["part_key"]})

    # ---- 4 characters
    chars, key_rows = [], []
    row_id = {}
    for r in tn:
        row, b = r["row"], rb[r["row"]]
        keys = r["character_keys"].split()
        cid = ID["character:" + row]
        row_id[row] = cid
        first = ex_c.get(keys[0]) if keys else None
        if keys and first is None:
            stop("character key %s is not in the export" % keys[0])
        pk = first["part_key"] if first else part_names[r["part_name"]]["part_key"]
        if part_names[r["part_name"]]["part_key"] != pk:
            stop("row %s: the part does not agree with the export" % row)
        c = cn.get(row, {})
        chars.append({"id": cid, "character_name_english": r["character_name_english"], "character_name_latin": r["character_name_latin"],
                      "character_name_as_written": r["character_name_as_written"], "also_written_as": r["also_written_as"],
                      "part_id": ID["part:" + pk], "part_name_as_written": r["part_name"], "group": r["group"], "kind": b["kind"], "type": b["type"], "unit": b["unit"],
                      "status": "proposed", "in_this_release": {"as written": "as in the list", "changed": "changed from the list", "new": "new"}[b["status"]],
                      "xde_item": b["xde_items"],
                      "pubchem_cid": c.get("registry_number_cid", ""), "inchikey": c.get("inchikey", ""), "chebi": c.get("chebi", ""),
                      "note": one_space(" ".join(t for t in (b["note"], c.get("note", "")) if t)),
                      "values_recorded": str(sum(int(ex_c[k]["use_recorded_values"] or 0) for k in keys)),
                      "origin": b["origin_title"], "mrdbid_character_keys": " ".join(keys), "_row": row, "_other": other(row)})
        for i, k in enumerate(keys):
            key_rows.append({"record": "character", "mrdbid_key": k, "id": cid, "note": "" if i == 0 else "a name joined into this character"})
    if sorted(k["mrdbid_key"] for k in key_rows) != sorted(ex_c):
        stop("the character keys of the export are not covered one for one")

    # ---- 5 value options
    vals = []
    for i, v in enumerate(vs):
        keys = v["value_option_keys"].split()
        vid = ID[vkey[i]]
        ex = [ex_v[k] for k in keys]
        desc = [e for e in ex if e["value_option_description"].strip()]
        src = v["source"]
        added = "in the list as written" if keys else ("added: one of Yes, No, Unknown, Not Tested" if "general list" in src else "added from " + src.replace("XDE item", "XDE's list, item"))
        vals.append({"id": vid, "character_id": row_id[v["row"]], "value_option_name": v["value_option_shown"], "value_option_as_written": v["value_option_as_written"] if keys else "",
                     "status": "proposed", "in_this_release": added,
                     "description_on_record": "yes" if desc else "", "description_source": "; ".join(sorted(set(e["origin_title"] for e in desc))),
                     "origin": "; ".join(sorted(set(e["origin_title"] for e in ex))), "values_recorded": str(sum(int(e["use_recorded_values"] or 0) for e in ex)),
                     "mrdbid_value_option_keys": " ".join(keys), "_row": v["row"], "_other": other(v["row"])})
        for j, k in enumerate(keys):
            key_rows.append({"record": "value option", "mrdbid_key": k, "id": vid, "note": "" if j == 0 else "the same words as another option of this character"})
    if sorted(k["mrdbid_key"] for k in key_rows if k["record"] == "value option") != sorted(ex_v):
        stop("the value option keys of the export are not covered one for one")
    key_rows = [{"record": "part", "mrdbid_key": p["mrdbid_part_key"], "id": p["id"], "note": ""} for p in parts] + key_rows

    # ---- 6 for the site, list one: spelling corrections inside the name as stored
    key_row = {k: r["row"] for r in tn for k in r["character_keys"].split()}
    chem_by = {c["as_written"]: c for c in chem_rules["compounds"]}
    S_KINDS, O_KINDS = set(rules["spelling_kinds"]), set(rules["other_kinds"])
    word_rules = [(e["from"], e["to"], e["kind"], e["why"]) for e in term_rules["spelling_names"] if e["kind"] in S_KINDS]
    word_rules.sort(key=lambda e: -len(e[0]))
    whole = {e["name"]: e for e in term_rules["name_fixes"]}
    old_words = {k: e for e in rules["rebuild_spelling_words"] for k in e["keys"]}
    spelling, corrected_as_stored = [], {}

    def term_fix(text):
        """the spelling settled by the term rules: a whole name, or word by word"""
        if text in whole:
            return whole[text]["to"], ["spelling"], [whole[text]["why"]]
        kinds, why = [], []
        for frm, to, kind, reason in word_rules:
            pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(frm) + r"(?![A-Za-z0-9])", re.I)
            if pat.search(text) and pat.sub(to, text) != text:
                text = pat.sub(to, text)
                kinds.append(kind); why.append(reason)
        return text, kinds, why
    for k in sorted(ex_c, key=int):
        stored, row = ex_c[k]["character_name"], key_row[k]
        new, why, kinds = stored, [], []
        if other(row):
            pass
        elif rb[row]["group"] == "chemical compound":
            w = stored.split()
            c = chem_by.get(" ".join(w[:-1]))
            if c is not None and w[-1] in ("present", "quantity") and c["kind"] in S_KINDS:
                new = c["shown"] + " " + w[-1]
                kinds, why = [c["kind"]], [c["why"]]
        else:
            if k in old_words:
                e = old_words[k]
                if e["from"] not in new:
                    stop("key %s: the word %r is not in the name as stored" % (k, e["from"]))
                new = new.replace(e["from"], e["to"])
                kinds.append("spelling"); why.append(e["basis"])
            new, k2, w2 = term_fix(new)
            kinds += k2; why += w2
        corrected_as_stored[k] = new
        if new != stored:
            spelling.append({"record": "character", "mrdbid_key": k, "id": row_id[row], "name_as_stored": stored, "name_corrected": new,
                             "kind": "; ".join(dict.fromkeys(kinds)), "basis": " ".join(dict.fromkeys(why))})
    vfix = {(e["row"], e["option"]): e for e in term_rules["spelling_values"]}
    vkey_row = {k: v["row"] for v in vs for k in v["value_option_keys"].split()}
    vkey_id = {k["mrdbid_key"]: k["id"] for k in key_rows if k["record"] == "value option"}
    used = set()
    for k in sorted(ex_v, key=int):
        e = vfix.get((vkey_row[k], ex_v[k]["value_option_name"]))
        if e:
            used.add((e["row"], e["option"]))
            spelling.append({"record": "value option", "mrdbid_key": k, "id": vkey_id[k], "name_as_stored": ex_v[k]["value_option_name"], "name_corrected": e["to"],
                             "kind": e.get("kind", "spelling"), "basis": e["why"]})
    if used != set(vfix):
        stop("a value option spelling rule found no stored value option: %s" % sorted(set(vfix) - used))

    # ---- 7 for the site, list two: new versions and links (everything that is not spelling)
    other_changes = []
    for c in changes:
        k, kind = c["character_key"], c["kind_of_change"]
        row = key_row.get(k, k)
        rec = {"from_list": "the rebuild", "record": "character, its value options" if kind.startswith("value option") else "character",
               "mrdbid_key": k if k in ex_c else "", "id": row_id.get(row, ""), "name_as_stored": ex_c[k]["character_name"] if k in ex_c else "",
               "kind": kind, "from": c["from"], "to": c["to"], "basis": c["basis"], "_other": other(row) if row in rb else False}
        plain = k in ex_c and rb[row]["group"] != "chemical compound" and not rec["_other"]
        if kind.startswith("name:") and plain:  # a change of name starts from the name with its spelling corrected and ends at one
            rec["from"] = corrected_as_stored[k] if c["from"] == ex_c[k]["character_name"] else term_fix(c["from"])[0]
            rec["to"] = term_fix(c["to"])[0]
        if kind in ("name: spelling", "name: mislabel and spelling"):
            if corrected_as_stored.get(k) == rec["to"]:
                continue  # spelling only: it is in list one
            rec.update({"kind": "name: words removed" if kind == "name: spelling" else "name: mislabel",
                        "basis": c["basis"] + " The spelling of the word is in the list of spelling corrections."})
        other_changes.append(rec)
    for v in vals:  # the value options that came with a new character
        if not v["mrdbid_value_option_keys"] and not v["_row"].isdigit():
            other_changes.append({"from_list": "the rebuild", "record": "character, its value options", "mrdbid_key": "", "id": row_id[v["_row"]], "name_as_stored": "",
                                  "kind": "value option added", "from": "", "to": v["value_option_name"], "basis": "With the new character; " + v["in_this_release"] + ".",
                                  "_other": False})
    for e in sp:
        if e["kind"] in O_KINDS:
            if e["where"] == "value option":  # the option that is kept and shown; its keys are those of both written forms
                kept = [v for v in vals if v["_row"] == e["row"] and v["value_option_name"] == e["to"]]
                if len(kept) != 1:
                    stop("row %s: the value option %r is not in the list once" % (e["row"], e["to"]))
                record, keys, rid = "value option", kept[0]["mrdbid_value_option_keys"].split(), kept[0]["id"]
                stored = " | ".join(ex_v[k]["value_option_name"] for k in keys)
            else:
                record, keys, rid = "character", next(r["character_keys"] for r in tn if r["row"] == e["row"]).split(), row_id[e["row"]]
                stored = " | ".join(ex_c[k]["character_name"] for k in keys)
            other_changes.append({"from_list": "the words", "record": record, "mrdbid_key": " ".join(keys), "id": rid, "name_as_stored": stored, "kind": e["kind"],
                                  "from": e["from"], "to": e["to"], "basis": e["why"], "_other": other(e["row"])})
    # what happened to a thing of the list is read from the two lists of changes, so the three cannot disagree
    sp_ids, oc_ids = set(e["id"] for e in spelling), set(e["id"] for e in other_changes if e["id"])
    for c in chars:
        if c["in_this_release"] == "new":
            continue
        if c["in_this_release"] == "changed from the list" and c["id"] not in oc_ids | sp_ids:
            stop("character %s was changed by the rebuild and has no row in either list of changes" % c["id"])
        c["in_this_release"] = "changed from the list" if c["id"] in oc_ids else ("spelling corrected" if c["id"] in sp_ids else "as in the list")
    for v in vals:
        if v["in_this_release"] == "in the list as written" and v["id"] in oc_ids | sp_ids:
            v["in_this_release"] = "in the list, shown once for two written forms" if v["id"] in oc_ids else "in the list, spelling corrected"
    n_sp_terms = sum(1 for e in sp if e["kind"] in S_KINDS)
    n_other_terms = sum(1 for e in sp if e["kind"] in O_KINDS)
    if n_sp_terms + n_other_terms != len(sp):
        stop("a kind in the spelling log is in neither list: %s" % sorted(set(e["kind"] for e in sp) - S_KINDS - O_KINDS))

    # ---- 8 left for users, sources
    LP = rules["left_for_users_public"]  # the file is written for a reader outside the workspace
    key_id = {k["mrdbid_key"]: k["id"] for k in key_rows if k["record"] == "character"}

    def rows_to_ids(text):
        m = re.fullmatch(r"rows? ([0-9, to]+)", text)
        if not m:
            return []
        rows = []
        for part in m.group(1).split(","):
            a, _, b = part.strip().partition(" to ")
            rows += [str(n) for n in range(int(a), int(b or a) + 1)]
        return [row_id[n] for n in rows]
    left, seen = [], set()
    for l in read_csv(os.path.join(R, "left_for_users.csv")):
        seen.add(l["topic"])
        if l["topic"] in LP["dropped"]:
            continue
        keys = l["character_keys"].split()
        left.append({"from_list": "the rebuild", "topic": l["topic"], "what_is_left": LP["text"].get(l["topic"], l["what"]), "where": LP["where"].get(l["topic"], ""),
                     "ids": " ".join(dict.fromkeys(key_id[k] for k in keys)), "character_names_as_written": l["character_names_as_written"],
                     "mrdbid_character_keys": l["character_keys"], "_other": any(other(key_row[k]) for k in keys if k in key_row)})
    for l in read_csv(os.path.join(T, "left_for_users.csv")):
        seen.add(l["id"])
        ids = rows_to_ids(l["where"])
        where = LP["where"].get(l["id"], "characters.csv" if ids else None)
        if where is None:
            stop("left for users, topic %s: the rules name no place in the release for %r" % (l["id"], l["where"]))
        if l["id"] in LP["ids_by_option"]:  # the characters concerned are found in the list itself
            pat = re.compile(LP["ids_by_option"][l["id"]])
            ids = list(dict.fromkeys(v["character_id"] for v in vals if not v["_other"] and pat.search(v["value_option_name"])))
        left.append({"from_list": "the words", "topic": l["id"] + " " + l["topic"], "what_is_left": LP["text"].get(l["id"], l["left"]), "where": where,
                     "ids": " ".join(ids), "_other": OL["starts_with"] in l["topic"]})
    unused = (set(LP["dropped"]) | set(LP["text"]) | set(LP["where"]) | set(LP["ids_by_option"])) - seen
    if unused:
        stop("left for users: the rules name a topic that is not in the working files: %s" % sorted(unused))
    S, PS = term_rules["sources"], rules["public_sources"]
    sources = [{"source": PS.get(k, {}).get("source", s["title"]), "license": PS.get(k, {}).get("license", s["license"]), "read": s["read"], "used_for": s["used_for"]}
               for k, s in S.items()]
    sources += [{"source": o["title"] + ((" (" + o["container"] + ")") if o["container"] else ""),
                 "license": "the first list: used by its author's permission" if o["title"] == rules["first_list"]["title"] else (o["license"] or "no reuse license on record"),
                 "read": "", "used_for": "origin recorded in the list for %s characters and %s value options" % (o["character_count"], o["value_option_count"])} for o in ex_o]
    sources += [dict(s) for s in rules["sources_added"]]
    for rows, cols in ((chars, ("note",)), (spelling, ("basis",)), (other_changes, ("basis", "from", "to")), (left, ("what_is_left", "where")), (sources, ("source", "license", "used_for"))):
        for r in rows:
            for c in cols:
                if c in r:
                    r[c] = public(r[c])
    dead = [rule[0].pattern for rule in PUBLIC if not rule[2]]
    if dead:
        stop("a rewording of the rules found nothing to reword: %s" % dead)
    for rows, cols in ((chars, ("note",)), (spelling, ("basis",)), (other_changes, ("basis",)), (left, ("what_is_left", "where"))):
        for r in rows:
            for c in cols:
                for pat, what in LEAKS:
                    if re.search(pat, r.get(c, "")):
                        stop("%s is in a text of the release: %r" % (what, r[c][:160]))
            for fn in re.findall(r"\b[a-z_]+\.csv\b", r.get("where", "")):
                if fn not in RELEASE_FILES:
                    stop("a file that is not in the release is named as a place: %s" % fn)

    # ---- 9 write
    out = os.path.join(HERE, version)
    oth = os.path.join(out, *OL["folder"].split("/"))
    CC, VC = ["id", "character_name_english", "character_name_latin", "character_name_as_written", "also_written_as", "part_id", "part_name_as_written", "group", "kind",
              "type", "unit", "status", "in_this_release", "xde_item", "pubchem_cid", "inchikey", "chebi", "note", "values_recorded", "origin",
              "mrdbid_character_keys"], ["id", "character_id", "value_option_name", "value_option_as_written", "status", "in_this_release", "description_on_record",
                                         "description_source", "origin", "values_recorded", "mrdbid_value_option_keys"]
    SC = ["record", "mrdbid_key", "id", "name_as_stored", "name_corrected", "kind", "basis"]
    OC = ["from_list", "record", "mrdbid_key", "id", "name_as_stored", "kind", "from", "to", "basis"]
    LC = ["from_list", "topic", "what_is_left", "where", "ids", "character_names_as_written", "mrdbid_character_keys"]
    mine = lambda rows: [r for r in rows if not r.get("_other")]
    theirs = lambda rows: [r for r in rows if r.get("_other")]
    write_csv(os.path.join(out, "parts.csv"), ["id", "part_name_english", "part_name_latin", "part_name_as_written", "display_order", "status", "mrdbid_part_key"], parts)
    write_csv(os.path.join(out, "characters.csv"), CC, mine(chars))
    write_csv(os.path.join(out, "value_options.csv"), VC, mine(vals))
    write_csv(os.path.join(out, "keys.csv"), ["record", "mrdbid_key", "id", "note"], key_rows)
    write_csv(os.path.join(out, "changes", "spelling_corrections.csv"), SC, spelling)
    write_csv(os.path.join(out, "changes", "new_versions_and_links.csv"), OC, mine(other_changes))
    write_csv(os.path.join(out, "left_for_users.csv"), LC, mine(left))
    write_csv(os.path.join(out, "sources.csv"), ["source", "license", "read", "used_for"], sources)
    write_csv(os.path.join(oth, "characters.csv"), CC, theirs(chars))
    write_csv(os.path.join(oth, "value_options.csv"), VC, theirs(vals))
    if theirs(other_changes):
        stop("a change would touch another source's words: %d rows" % len(theirs(other_changes)))
    write_csv(os.path.join(oth, "left_for_users.csv"), LC, theirs(left))
    write_csv(reg_path, ["id", "kind", "key", "first_release", "status", "replaced_by"], register)
    if any(r.get("_other") for r in spelling):
        stop("a spelling correction would touch another source's words")
    by_char = collections.defaultdict(list)
    for v in mine(vals):
        by_char[v["character_id"]].append({"id": v["id"], "label": v["value_option_name"], "as_written": v["value_option_as_written"], "status": v["status"]})
    doc = {"name": "Mushroom Character Vocabulary", "version": version, "prepared": rules["prepared"], "identifier_base": rules["identifiers"]["base"],
           "license": rules["license_data"], "status": rules["status_line"], "consumption": rules["consumption_line"],
           "parts": [{"id": p["id"], "labels": {"en-US": p["part_name_english"], "la": p["part_name_latin"]}, "as_written": p["part_name_as_written"]} for p in parts],
           "characters": [{"id": c["id"], "labels": {"en-US": c["character_name_english"], "la": c["character_name_latin"]},
                           "as_written": [n for n in [c["character_name_as_written"]] + [a.strip() for a in c["also_written_as"].split("|")] if n],
                           "part": c["part_id"], "group": c["group"], "kind": c["kind"], "type": c["type"], "unit": c["unit"], "status": c["status"],
                           "pubchem_cid": c["pubchem_cid"], "inchikey": c["inchikey"], "chebi": c["chebi"], "value_options": by_char.get(c["id"], [])} for c in mine(chars)]}
    write_text(os.path.join(out, "vocabulary.json"), json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    every_rule = sorted([(e["from"], e["to"]) for e in term_rules["spelling_names"]], key=lambda e: -len(e[0]))

    def settled(text):
        """the name once every listed change is made: the spelling corrections and the word rules of the second list"""
        if text in whole:
            return whole[text]["to"]
        for frm, to in every_rule:
            text = re.sub(r"(?<![A-Za-z0-9])" + re.escape(frm) + r"(?![A-Za-z0-9])", to, text, flags=re.I)
        return text
    no_license = set(o["title"] for o in ex_o if not o["license"].strip() and o["title"] != rules["first_list"]["title"])

    def unlicensed(v):  # a value option whose name the list took from a book or a website that states no reuse license
        return any(t in no_license for t in v["origin"].split("; "))
    counts = {"identifiers": len(register), "parts": len(parts), "characters": len(chars), "characters_cc0": len(mine(chars)), "characters_other_license": len(theirs(chars)),
              "value_options": len(vals), "value_options_cc0": len(mine(vals)), "value_options_other_license": len(theirs(vals)),
              "character_names_that_differ_english_latin": sum(1 for c in chars if c["character_name_english"] != c["character_name_latin"]),
              "characters_with_an_item_of_the_first_list": sum(1 for c in mine(chars) if c["xde_item"]), "characters_with_registry_number": sum(1 for c in chars if c["pubchem_cid"]),
              "value_options_in_the_list": sum(1 for v in vals if v["mrdbid_value_option_keys"]), "value_options_added": sum(1 for v in vals if not v["mrdbid_value_option_keys"]),
              "value_option_descriptions_on_record_not_reissued": sum(1 for v in vals if v["description_on_record"]),
              "keys_parts": len(ex_p), "keys_characters": len(ex_c), "keys_value_options": len(ex_v),
              "spelling_corrections": len(spelling), "spelling_corrections_characters": sum(1 for s in spelling if s["record"] == "character"),
              "spelling_corrections_value_options": sum(1 for s in spelling if s["record"] == "value option"),
              "new_versions_and_links": len(mine(other_changes)), "new_versions_and_links_other_license": len(theirs(other_changes)),
              "new_versions_and_links_by_kind": dict(sorted(collections.Counter(c["kind"] for c in other_changes).items())),
              "latin_names_in_a_display_form": sum(1 for r in tn if r["group"] != "chemical compound" and not other(r["row"])
                                                   and r["character_name_latin"] != settled(r["character_name_rebuilt"])),
              "value_option_names_from_a_source_without_a_license": sum(1 for v in mine(vals) if unlicensed(v)),
              "value_option_names_from_such_a_source_of_more_than_three_words": sum(1 for v in mine(vals) if unlicensed(v) and len(re.findall(r"[A-Za-z0-9']+", v["value_option_name"])) > 3),
              "left_for_users_rows": len(left), "sources": len(sources)}
    if counts["characters_cc0"] + counts["characters_other_license"] != len(tn) or counts["value_options_cc0"] + counts["value_options_other_license"] != len(vs):
        stop("the two license groups do not add up to the list")
    I = rules["identifiers"]
    first, last = register[0]["id"], register[-1]["id"]
    readme = """# Mushroom Character Vocabulary, release {version}

Prepared {prepared}. {status}

{mission}

## What this is
A list of the characters used to describe mushrooms: the parts of a mushroom, the characters of each part, and the
value options of each character. Every one has a permanent identifier. The list is the whole character list of the
MRDBID database as exported on 2026-11-19, rebuilt against the list it was first parsed from, with the spelling
settled and every character named in United States English and in the scientific (Latin) form.

| | |
|---|---|
| Identifiers | {identifiers} ({first} to {last}) |
| Parts | {parts} |
| Characters | {characters} ({characters_cc0} in the open list, {characters_other_license} under another source's license) |
| Value options | {value_options} ({value_options_cc0} in the open list, {value_options_other_license} under another source's license) |
| Character names that differ between English and Latin | {character_names_that_differ_english_latin} |
| Characters of a chemical compound with a registry number | {characters_with_registry_number} |

## The identifiers
{form} Written in full: {base}MCV_0000001.
{id_rules}

## License
{license_data} for the files of the open list. {license_note}
- `{folder}/` holds {characters_other_license} characters and {value_options_other_license} value options whose words are another source's: {credit} License: {license} {rule}
- {value_option_descriptions_on_record_not_reissued} value options have a description on record that was taken from a book or a website for which no reuse
  license is on record. The description is not in this release. `value_options.csv` names its source.
- The name of a value option is listed with the source the list took it from. {value_option_names_from_a_source_without_a_license} names
  come from a book or a website for which no reuse license is on record. Most are a single term of the field, such as a word
  for a shape; {value_option_names_from_such_a_source_of_more_than_three_words} are longer: a term with a few words of explanation, or a short phrase, like
  "Farinaceous (like fresh meal)".

## Consumption
{consumption}

## The files
- `parts.csv`, `characters.csv`, `value_options.csv` — the open list. Each row: the identifier, the name shown and
  the name as written; a character and a value option also say where they came from. A character carries its
  English and its Latin name; where they are the same the word has one form. The two names are display forms and are not in the lists of changes: {latin_names_in_a_display_form}
  Latin names differ from the name in the list in the form of a word (lamellae for lamella), in showing one of two
  words the list wrote side by side (context for "context flesh"), or in the scientific word for a plain one (stipe
  for stem).
  `xde_item` is the number of the item of the first list that the character was parsed from or matches. The
  sentences of that list are not carried in this release.
- `vocabulary.json` — the same list in one file, with the names tagged en-US and la.
- `keys.csv` — the key of every part, character and value option in the MRDBID database, with its identifier.
  {keys_characters} character keys and {keys_value_options} value option keys; a name joined into another character
  carries that character's identifier.
- `changes/spelling_corrections.csv` — {spelling_corrections} corrections of spelling inside a name as stored: letters, capital
  letters, hyphens and other marks, spaces. Nothing else about the name changes in this list.
- `changes/new_versions_and_links.csv` — {new_versions_and_links} changes that are more than spelling: words removed or added, names joined,
  value options added, a unit or a type set. Each names its basis. `name_as_stored` is the name in the MRDBID
  database; `from` and `to` are the change itself, which may start from a name already changed by another row.
- `left_for_users.csv` — what no source decides. It is shown as written and left for the people who use the list.
- `sources.csv` — every source used, with its license or what is known of it.
- `{folder}/` — the words of another source, under that source's license.
- `MANIFEST.json` — the counts and a checksum of every file.

## Credits
The first list: "{fl_title}", {fl_where}. Most of the characters were parsed from it. In these files "{fl_tag}" is the
short tag of that list. {fl_credit}
Compiled by Will Johnston. Built with Claude (Anthropic).
""".format(fl_title=rules["first_list"]["title"], fl_where=rules["first_list"]["where"], fl_tag=rules["first_list"]["tag"], fl_credit=rules["first_list"]["credit"],
           version=version, prepared=rules["prepared"], status=rules["status_line"], mission=rules["mission"], first=first, last=last, form=I["form"], base=I["base"],
           id_rules="\n".join("- " + r for r in I["rules"]), license_data=rules["license_data"], license_note=rules["license_note"], folder=OL["folder"],
           credit=OL["credit"], license=OL["license"], rule=OL["rule"], consumption=rules["consumption_line"], **counts)
    write_text(os.path.join(out, "README.md"), readme)
    write_text(os.path.join(out, "LICENSE.md"), """# License of release {version}

To the extent possible under law, Will Johnston has waived all copyright and related or neighboring rights to the
files of the open list of the Mushroom Character Vocabulary, release {version}: parts.csv, characters.csv,
value_options.csv, vocabulary.json, keys.csv, the two files under changes/, left_for_users.csv, sources.csv, and
the register of identifiers. This is the CC0 1.0 Universal dedication: https://creativecommons.org/publicdomain/zero/1.0/

{license_note}

Not covered: the files under `{folder}/`. Their words are the authors' and keep the authors' license, as stated in
that folder.
""".format(version=version, license_note=rules["license_note"], folder=OL["folder"]))
    write_text(os.path.join(oth, "README.md"), """# Words of another source: FungalTraits

{n_c} characters and {n_v} value options of the list are trait names and trait values of FungalTraits. They have
identifiers of the Mushroom Character Vocabulary, and their words stay the authors'.

Credit: {credit}
License: {license}
{rule}

These files are not under CC0.
""".format(n_c=counts["characters_other_license"], n_v=counts["value_options_other_license"], credit=OL["credit"], license=OL["license"], rule=OL["rule"]))
    for root, _, names in os.walk(out):  # the guard: no path of the workspace in any file of the release
        for fn in names:
            text = io.open(os.path.join(root, fn), encoding="utf-8").read()
            if re.search(r"(MRDBID|Claude_AI)/|/Users/|/home/", text):
                stop("a path of the workspace is in %s" % fn)
    files = {}
    for root, _, names in os.walk(out):
        for fn in sorted(names):
            if fn == "MANIFEST.json":
                continue
            p = os.path.join(root, fn)
            files[os.path.relpath(p, out).replace(os.sep, "/")] = {"bytes": os.path.getsize(p), "sha256": sha256(p)}
    man = {"what": "Mushroom Character Vocabulary, release %s: permanent identifiers for the whole list; a release candidate until it is published" % version,
           "built_from": {"export": name, "characters_two_names_sha256": sha256(os.path.join(T, "characters_two_names.csv")),
                          "value_options_spelling_sha256": sha256(os.path.join(T, "value_options_spelling.csv")),
                          "characters_rebuilt_sha256": sha256(os.path.join(R, "characters_rebuilt.csv")), "export_manifest_sha256": sha256(os.path.join(E, "MANIFEST.json"))},
           "rules": {"file": "releases/release_rules.json", "sha256": sha256(rules_path)},
           "register": {"file": "releases/identifiers.csv", "sha256": sha256(reg_path), "identifiers": len(register)},
           "made_by": {"tool": "releases/build_release.py", "sha256": sha256(os.path.abspath(__file__))},
           "run_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "counts": counts, "files": dict(sorted(files.items()))}
    write_text(os.path.join(out, "MANIFEST.json"), json.dumps(man, ensure_ascii=False, indent=1) + "\n")
    print("release %s: %d identifiers (%d parts, %d characters, %d value options); %d spelling corrections, %d other changes" % (
        version, len(register), len(parts), len(chars), len(vals), len(spelling), len(other_changes)))


if __name__ == "__main__":
    main()
