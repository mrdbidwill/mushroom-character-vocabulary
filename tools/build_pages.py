#!/usr/bin/env python3
"""Build the identifier pages of the Mushroom Character Vocabulary (GitHub Pages, folder docs/).

One page per identifier in releases/identifiers.csv, read from the newest release folder.
https://w3id.org/mcv/MCV_0000001 redirects to the GitHub Pages copy of docs/id/MCV_0000001.html.
Reads the release; never changes it. MIT License (see LICENSE.md).
From release 1.1.0: the disclaimer at the top and bottom of every page (the shared disclaimer style) and beside items about
chemistry or toxicity and references whose subject includes eating or using fungi; definitions, units, links and a
references page when the release has them.
Usage: python3 tools/build_pages.py [release_version]
"""
import csv
import re
import html
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "https://github.com/mrdbidwill/mushroom-character-vocabulary"
BASE = "https://w3id.org/mcv/"

CSS = """body{font-family:system-ui,-apple-system,sans-serif;max-width:52rem;margin:2rem auto;padding:0 1rem;line-height:1.5;color:#1d1d1d}
a{color:#1a5c8a}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;padding:.3rem .5rem;text-align:left;vertical-align:top}
th{width:14rem;font-weight:600}code{font-size:.95em}.note{color:#555;font-size:.9em}h1{font-size:1.6rem}
.disclaimer{background:#fff4e0;border-left:4px solid #8a4b00;padding:.4rem .7rem;color:#3b2a10;margin:.6rem 0}
.disclaimer strong{font-weight:700}.disclaimer.near{font-size:.9em;margin:.3rem 0 .2rem}
blockquote{margin:.2rem 0;padding-left:.6rem;border-left:3px solid #ccc}"""

# The one disclaimer of Will Johnston's sites (shared_reference/disclaimer/disclaimer.json), "This site" made
# "This vocabulary". Kept here word for word so the pages build from the repository alone.
LEAD = "No advice about consumption."
FULL = ("This vocabulary reports how sources describe fungi. It is not a guide to eating, using or handling any "
        "fungus, and nothing here says whether any fungus is safe. Values about chemistry or toxicity are reported "
        "only as their source states them.")
NEAR = "This is listed for how it describes fungi. Listing it is not advice to eat, use or handle any fungus."
DISC = f'<p class="disclaimer"><strong>{LEAD}</strong> {FULL}</p>'
DISC_NEAR = f'<p class="disclaimer near"><strong>{LEAD}</strong> {NEAR}</p>'


def near_item(c):
    """A character whose subject is chemistry or toxicity."""
    return c.get("group") == "chemical compound" or c.get("kind") in ("toxicity", "chemical named by its effect")


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def e(s):
    return html.escape(s or "")


def page(title, body, version, depth):
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} — Mushroom Character Vocabulary</title><link rel="stylesheet" href="{up}style.css"></head>
<body>{DISC}<p class="note"><a href="{up}index.html">Mushroom Character Vocabulary</a>, release {e(version)}</p>
{body}
<p class="note">Status of every entry: proposed. Source files, licenses and the register:
<a href="{REPO}">{REPO}</a>. Words shown as the release holds them.</p>
{DISC}
</body></html>
"""


def rows(pairs):
    return "<table>" + "".join(
        f"<tr><th>{e(k)}</th><td>{v}</td></tr>" for k, v in pairs if v) + "</table>"


def link(i, label):
    return f'<a href="{i}.html">{e(label)}</a> <code>{e(i)}</code>'


def main():
    rel_dir = os.path.join(ROOT, "releases")
    versions = sorted((d for d in os.listdir(rel_dir) if os.path.isdir(os.path.join(rel_dir, d))),
                      key=lambda d: [int(x) for x in d.split('.')])
    version = sys.argv[1] if len(sys.argv) > 1 else versions[-1]
    src = os.path.join(rel_dir, version)
    ft = os.path.join(src, "other_licenses", "fungaltraits")

    parts = {r["id"]: r for r in read(os.path.join(src, "parts.csv"))}
    chars, vos = {}, {}
    for d, lic in ((src, "CC0 1.0"), (ft, "FungalTraits (other_licenses/fungaltraits/)")):
        for r in read(os.path.join(d, "characters.csv")):
            r["_license"] = lic
            chars[r["id"]] = r
        for r in read(os.path.join(d, "value_options.csv")):
            r["_license"] = lic
            vos[r["id"]] = r
    register = read(os.path.join(rel_dir, "identifiers.csv"))
    register = [r for r in register if [int(x) for x in r["first_release"].split(".")] <= [int(x) for x in version.split(".")]]

    def opt(name):
        p = os.path.join(src, name)
        return read(p) if os.path.exists(p) else []
    defs, units, links, refs = opt("definitions.csv"), opt("units.csv"), opt("links.csv"), opt("references.csv")
    d_by = {}
    d_rec = {d["record"]: d for d in defs}
    for d in defs:
        d_by.setdefault(d["target_id"], []).append(d)
    u_by = {u["character_id"]: u for u in units}
    l_by = {}
    for l in links:
        l_by.setdefault(l["from_id"], []).append((l, l["to_id"], l["to_name"]))
        l_by.setdefault(l["to_id"], []).append((l, l["from_id"], l["from_name"]))
    r_by = {}
    for r in refs:
        for i in r.get("cited_for_ids", "").split():
            r_by.setdefault(i, []).append(r)

    def def_html(i):
        ds = d_by.get(i, [])
        if not ds:
            return ""
        out = "<h2>Definitions</h2><ul>"
        for d in ds:
            src_name = {"KAUFFMAN1918": "Kauffman 1918, The Agaricaceae of Michigan"}.get(d["source"], d["source"])
            where = ", ".join(x for x in (src_name, d["source_id"], d["source_headword"],
                                          f"p. {d['page']}" if d["page"] else "") if x)
            out += f"<li><em>{e(d['relation'])}</em>: {e(where)}"
            if d["text"]:
                out += f"<blockquote>{e(d['text'])}</blockquote>"
            if d["note"]:
                out += f'<div class="note">{e(d["note"])}</div>'
            out += f'<div class="note">Record {e(d["record"])}; {e(d["license"])}; {e(d["checked"])}</div></li>'
        return out + "</ul>"

    def links_html(i):
        ls = l_by.get(i, [])
        if not ls:
            return ""
        return "<h2>Links</h2><ul>" + "".join(
            f'<li><em>{e(l["relation"])}</em> {link(o, n)}<div class="note">{e(l["basis"])}</div></li>'
            for l, o, n in ls) + "</ul>"

    def refs_html(i):
        rs = r_by.get(i, [])
        if not rs:
            return ""
        return "<h2>References</h2><ul>" + "".join(
            f'<li>{e(r["title"])}' + (f' <a href="{e(r["identifier"])}">{e(r["identifier"])}</a>' if r["identifier"].startswith("http") else "")
            + f'<div class="note">{e(r["cited_how"] or r["use"])}</div></li>' for r in rs) + "</ul>"

    out = os.path.join(ROOT, "docs")
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "id"))
    with open(os.path.join(out, "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS)
    open(os.path.join(out, ".nojekyll"), "w").close()

    by_part, by_char = {}, {}
    for c in chars.values():
        by_part.setdefault(c["part_id"], []).append(c)
    for v in vos.values():
        by_char.setdefault(v["character_id"], []).append(v)

    def lic_line(lic):
        if lic.startswith("CC0"):
            return '<a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>'
        return (f'Not CC0. Words of FungalTraits (Põlme et al. 2020, doi:10.1007/s13225-020-00466-2), '
                f'CC BY-NC as a university repository lists it; not confirmed with the authors. '
                f'See <a href="{REPO}/tree/main/releases/{e(version)}/other_licenses/fungaltraits">its folder</a>.')

    written = 0
    for reg in register:
        i, kind = reg["id"], reg["kind"]
        if reg["status"] not in ("proposed",):
            body = f"<h1><code>{e(i)}</code></h1>" + rows([
                ("Status", e(reg["status"])),
                ("Replaced by", link(reg["replaced_by"], reg["replaced_by"]) if reg["replaced_by"] else ""),
            ])
        elif kind == "part":
            p = parts[i]
            cs = sorted(by_part.get(i, []), key=lambda c: c["character_name_english"].lower())
            body = f"<h1>{e(p['part_name_english'])}</h1>" + rows([
                ("Identifier", f"<code>{BASE}{e(i)}</code>"),
                ("Kind", "part"),
                ("Name (English)", e(p["part_name_english"])),
                ("Name (Latin)", e(p["part_name_latin"])),
                ("As written", e(p["part_name_as_written"])),
                ("License (this entry)", lic_line("CC0")),
            ]) + def_html(i) + "<h2>Characters</h2><ul>" + "".join(
                f"<li>{link(c['id'], c['character_name_english'])}</li>" for c in cs) + "</ul>"
        elif kind == "character":
            c = chars[i]
            vs = sorted(by_char.get(i, []), key=lambda v: v["value_option_name"].lower())
            p = parts.get(c["part_id"], {})
            body = f"<h1>{e(c['character_name_english'])}</h1>" + rows([
                ("Identifier", f"<code>{BASE}{e(i)}</code>"),
                ("Kind", "character"),
                ("Name (English)", e(c["character_name_english"])),
                ("Name (Latin)", e(c["character_name_latin"])),
                ("As written", e(c["character_name_as_written"])),
                ("Also written as", e(c["also_written_as"])),
                ("Part", link(c["part_id"], p.get("part_name_english", c["part_id"]))),
                ("Group", e(c["group"])), ("Kind of character", e(c["kind"])),
                ("Type", e(c["type"])), ("Unit", e(c["unit"])),
                ("Unit (UO)", (f'<a href="http://purl.obolibrary.org/obo/{e(u_by[i]["uo_id"].replace(":", "_"))}">'
                               f'{e(u_by[i]["uo_id"])}</a> {e(u_by[i]["uo_name"])}') if i in u_by else ""),
                ("PubChem CID", e(c["pubchem_cid"])), ("InChIKey", e(c["inchikey"])), ("ChEBI", e(c["chebi"])),
                ("In this release", e(c["in_this_release"])),
                ("Item of the first list", e(c["xde_item"])),
                ("Note", e(c["note"])),
                ("Origin", e(c["origin"])),
                ("License (this entry)", lic_line(c["_license"]) + (
                    '; the UO identifier and unit name: <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, '
                    'Units of Measurement Ontology' if i in u_by else "")),
            ]) + (DISC_NEAR if near_item(c) else "") + def_html(i) + links_html(i) + refs_html(i) + ("<h2>Value options</h2><ul>" + "".join(
                f"<li>{link(v['id'], v['value_option_name'])}</li>" for v in vs) + "</ul>" if vs else "")
        else:
            v = vos[i]
            c = chars.get(v["character_id"], {})
            body = f"<h1>{e(v['value_option_name'])}</h1>" + rows([
                ("Identifier", f"<code>{BASE}{e(i)}</code>"),
                ("Kind", "value option"),
                ("Name", e(v["value_option_name"])),
                ("As written", e(v["value_option_as_written"])),
                ("Character", link(v["character_id"], c.get("character_name_english", v["character_id"]))),
                ("In this release", e(v["in_this_release"])),
                ("Description", f"on record, not reissued; source: {e(v['description_source'])}"
                 if v["description_on_record"] else ""),
                ("Origin", e(v["origin"])),
                ("License (this entry)", lic_line(v["_license"])),
            ]) + (DISC_NEAR if near_item(c) else "") + def_html(i) + links_html(i)
        title = f"{i} {re.sub('<[^>]+>', '', body.split('</h1>')[0].split('<h1>')[1])}"
        with open(os.path.join(out, "id", f"{i}.html"), "w", encoding="utf-8") as f:
            f.write(page(title, body, version, 1))
        written += 1

    plist = sorted(parts.values(), key=lambda p: int(p["display_order"]))
    body = (f"<h1>Mushroom Character Vocabulary</h1>"
            f"<p>Release {e(version)}: {len(register)} identifiers, {len(parts)} parts, {len(chars)} characters, "
            f"{len(vos)} value options. Each identifier is written in full as <code>{BASE}MCV_0000001</code>.</p>"
            f"<p>Files, licenses and the register: <a href=\"{REPO}\">{REPO}</a></p><h2>Parts</h2><ul>"
            + "".join(f'<li><a href="id/{p["id"]}.html">{e(p["part_name_english"])}</a> <code>{e(p["id"])}</code></li>' for p in plist) + "</ul>"
            + (f'<h2>References</h2><p><a href="references.html">{len(refs)} references</a> of this release.</p>' if refs else ""))
    if refs:
        rb = "<h1>References</h1><p>The references of this release (references.csv). A title is cited, not copied; each work keeps its own license.</p>"
        sec = None
        for r in refs:
            if r["section"] != sec:
                sec = r["section"]
                rb += f"<h2>{e(sec)}</h2>"
            ids = " ".join(f'<a href="id/{e(x)}.html"><code>{e(x)}</code></a>' for x in r["cited_for_ids"].split())
            rb += (f'<div><p><strong>{e(r["title"])}</strong>' + (f' — {e(r["authors"])}' if r["authors"] else "")
                   + (f' <a href="{e(r["identifier"])}">{e(r["identifier"])}</a>' if r["identifier"].startswith("http") else (f" {e(r['identifier'])}" if r["identifier"] else ""))
                   + f'<br><span class="note">{e(r["cited_how"] or r["use"])}' + (f"; {e(r['license'])}" if r["license"] else "") + "</span>"
                   + (f"<br>{ids}" if ids else "") + "</p>"
                   + (DISC_NEAR if r.get("consumption_notice") == "yes" else "") + "</div>")
        with open(os.path.join(out, "references.html"), "w", encoding="utf-8") as f:
            f.write(page("References", rb, version, 0))
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(page("Index", body, version, 0))
    print(f"release {version}: {written} identifier pages, 1 index")


if __name__ == "__main__":
    main()
