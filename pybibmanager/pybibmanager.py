from difflib import SequenceMatcher
import re
import os
import regex
import argparse
from pathlib import Path
from typing import Dict, List, Set, Union
import bibtexparser
from bibtexparser.bparser import BibTexParser


def find_tex_files(directory: str) -> List[str]:
    tex_files = []
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.tex'):
                tex_files.append(os.path.join(dirpath, filename))
    return tex_files


def find_citations(tex_files: List[Path]) -> Set[str]:
    citations = set()
    citation_pattern = regex.compile(r"(?<!\\)%.+(*SKIP)(*FAIL)|\\(?:no)?citep?\{(?P<author>(?!\*)[^{}]+)\}")

    for file_name in tex_files:
        with open(file_name, 'r') as f:
            content = f.read()
            cited_keys = citation_pattern.findall(content)

            for keys in cited_keys:
                keys = regex.sub(r'\s+', '', keys)
                citations.update(keys.split(','))
    return citations


def parse_bibtex(bibtex_content: str) -> bibtexparser.bibdatabase.BibDatabase:
    parser = BibTexParser(common_strings=True)
    bib_database = bibtexparser.loads(bibtex_content, parser)
    return bib_database


def levenshtein_ratio_and_distance(s, t):
    seq_matcher = SequenceMatcher(None, s, t)
    return seq_matcher.ratio()


def detect_duplicates(entries: bibtexparser.bibdatabase.BibDatabase) -> bibtexparser.bibdatabase.BibDatabase:
    def compare_entries(entry1, entry2) -> bool:
        keys1 = set(entry1.keys())
        keys2 = set(entry2.keys())

        common_keys = keys1 & keys2
        threshold = 0.9

        for key in common_keys:
            if levenshtein_ratio_and_distance(entry1[key].lower(), entry2[key].lower()) < threshold:
                return False

        similarity_ratio = len(common_keys) / max(len(keys1), len(keys2))
        return similarity_ratio >= 0.7

    def format_entry(entry):
        formatted_entry = f"@{entry['ENTRYTYPE']}{{{entry['ID']},\n"
        for field, value in entry.items():
            if field not in {'ID', 'ENTRYTYPE'}:
                formatted_entry += f"  {field} = {{{value}}},\n"
        formatted_entry += "}\n"
        return formatted_entry

    def entry_fullness(entry):
        return len(entry.keys())

    unique_entries = bibtexparser.bibdatabase.BibDatabase()
    unique_entries.entries = []
    checked_entries = []

    for entry in entries.entries:
        duplicates = [entry]

        for existing_entry in checked_entries:
            if compare_entries(existing_entry, entry):
                duplicates.append(existing_entry)

        if len(duplicates) > 1:
            duplicates.sort(key=entry_fullness, reverse=True)
            print(f"\nFound duplicates:")
            for i, dup_entry in enumerate(duplicates):
                print(f"{i + 1}.\n{format_entry(dup_entry)}")

            choices = []
            while not choices:
                user_input = input(f"Choose the entries to keep (1-{len(duplicates)}) (separate by commas): ")
                try:
                    choices = [int(choice) - 1 for choice in user_input.split(',') if 0 < int(choice) <= len(duplicates)]
                    if not choices:
                        print("Invalid input. Please enter at least one valid number.")
                except ValueError:
                    print("Invalid input. Please enter valid numbers separated by commas.")

            for choice in choices:
                if duplicates[choice] not in unique_entries.entries:
                    unique_entries.entries.append(duplicates[choice])
        else:
            unique_entries.entries.append(entry)

        checked_entries.append(entry)

    return unique_entries


def process_bib_file(bib_file: str, citations: Set[str], remove_unused: bool, remove_duplicates: bool) -> None:
    with open(bib_file, 'r') as f:
        bibtex_content = f.read()

    bib_database = parse_bibtex(bibtex_content)

    if remove_unused:
        lower_citations = {citation.lower() for citation in citations}
        bib_database.entries = [
            entry for entry in bib_database.entries
            if entry['ID'].lower() in lower_citations]
    if remove_duplicates:
        bib_database = detect_duplicates(bib_database)

    with open(f"{bib_file}.new", 'w') as f:
        bibtexparser.dump(bib_database, f)


def main():
    parser = argparse.ArgumentParser(description="Process .bib files to remove unused and/or duplicate entries.")
    parser.add_argument('--remove-unused', action='store_true', help='Remove unused entries from .bib file.')
    parser.add_argument('--remove-duplicates', action='store_true', help='Remove duplicate entries from .bib file.')
    parser.add_argument('-b', '--bib-file', type=str, required=True, help='The path to the .bib file.')
    parser.add_argument('-t', '--tex-dir', type=str, required=True, help='The directory containing .tex files.')
    args = parser.parse_args()

    if not (args.remove_unused or args.remove_duplicates):
        print("No action specified. Please use '--remove-unused' and/or '--remove-duplicates' options.")
        return

    bib_file = args.bib_file
    tex_directory = args.tex_dir

    tex_files = find_tex_files(tex_directory)
    print(f"Searching for citations in files: {', '.join(map(str, tex_files))}")
    citations = find_citations(tex_files)
    print(f"Number of citations found: {len(citations)}")
    print(f"Found citations: {', '.join(citations)}")
    process_bib_file(bib_file, citations, args.remove_unused, args.remove_duplicates)

if __name__ == '__main__':
    main()
