import argparse
import os
import json
import lxml.etree as et
from from_tei import (
    add_underdot_to_unclear_letters,
    get_file,
    get_verse_as_tuple,
    parse,
    pre_parse_cleanup,
    remove_unclear_tags,
    tei_ns,
)
from to_json import save_tx, verse_to_dict


def get_siglum(root: et._Element) -> str:
    titles = root.xpath("//tei:title", namespaces={"tei": tei_ns})
    for title in titles:
        if title.get("n"):
            siglum = title.get("n")
            siglum = siglum.replace("-ns", "")
            break
        else:
            siglum = ""
    return siglum


def get_hands(root: et._Element) -> list:
    rdgs = root.xpath("//tei:rdg", namespaces={"tei": tei_ns})
    hands = []
    for rdg in rdgs:
        if rdg.get("hand") and rdg.get("hand") not in hands:
            hands.append(rdg.get("hand"))
    if hands == []:
        hands = ["firsthand"]
    return hands


def tei_to_json(tei: str, output_dir, single_verse: str, siglum_suffix: str):
    text = get_file(tei)
    text = pre_parse_cleanup(text)
    parsed, root = parse(text)
    add_underdot_to_unclear_letters(root)
    text = et.tostring(root, encoding="unicode")
    text = remove_unclear_tags(text)
    _, root = parse(text)
    hands = get_hands(root)
    siglum = get_siglum(root)
    if siglum_suffix:
        siglum = f"{siglum}-{siglum_suffix}"
    output_dir = f"{output_dir}/{siglum}"
    metadata = {"id": siglum, "siglum": siglum}
    verses = root.xpath(f"//tei:ab", namespaces={"tei": tei_ns})
    for verse in verses:
        ref = verse.get("n")
        if single_verse != "" and single_verse != ref:
            continue
        witnesses = get_verse_as_tuple(verse, hands=hands)
        verse_as_dict = verse_to_dict(siglum, ref, witnesses)
        save_tx(verse_as_dict, ref, output_dir)
    if output_dir:
        f = f"{output_dir}/metadata.json"
    else:
        f = "metadata.json"
    with open(f, "w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False)
    return True



def process_files(in_dir, out_dir, siglum_suffixes):
    for siglum_suffix in siglum_suffixes:

        siglum_in_dir = os.path.join(in_dir, siglum_suffix)

        tei_files = []

        for root, _, files in os.walk(siglum_in_dir):
            for file in files:
                if file.endswith(".xml"):
                    tei_files.append(os.path.join(root, file))

        for file_path in tei_files:
            try:
                tei_to_json(file_path, out_dir, "", siglum_suffix)
            except Exception as e:
                print(f"Conversion failed for {file_path}:", e)


def main():
    parser = argparse.ArgumentParser(
        description="Convert TEI XML files to JSON format."
    )
    parser.add_argument(
        "in_dir", type=str, help="Input directory containing TEI XML files."
    )
    parser.add_argument(
        "out_dir", type=str, help="Output directory for the JSON files."
    )
    parser.add_argument(
        "siglum_suffixes",
        type=str,
        nargs="+",
        help="List of siglum suffixes to process.",
    )

    args = parser.parse_args()

    process_files(args.in_dir, args.out_dir, args.siglum_suffixes)


if __name__ == "__main__":
    main()
