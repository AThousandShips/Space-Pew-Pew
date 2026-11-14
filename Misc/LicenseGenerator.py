#!/usr/bin/env python3

import json
import sys

if len(sys.argv) != 3:
    print("Invalid usage of LicenseGenerator.py, it should be called with a path to two files.")
    sys.exit(1)


TITLE_ATTRIBUTE_NAME = "title"
URL_ATTRIBUTE_NAME = "url"
LINK_ATTRIBUTE_NAME = "link"
TEXT_ATTRIBUTE_NAME = "text"
ELEMENTS_ATTRIBUTE_NAME = "elements"
FILES_ATTRIBUTE_NAME = "files"
FROM_ATTRIBUTE_NAME = "from"
FROM_URL_ATTRIBUTE_NAME = "from_url"
AUTHOR_ATTRIBUTE_NAME = "author"
AUTHOR_URL_ATTRIBUTE_NAME = "author_url"
SOURCE_ATTRIBUTE_NAME = "source"
TRANSLATE_ATTRIBUTE_NAME = "translate"
TRANSLATE_FROM_ATTRIBUTE_NAME = "translate_from"
TRANSLATE_AUTHOR_ATTRIBUTE_NAME = "translate_author"

LINK_PLAIN_TEMPLATE = "[{0}]"
LINK_TEMPLATE = "[{1}]({0})"

SUPER_SECTION_TEMPLATE = "# {0}\n\n"
SECTION_TEMPLATE = "## {0}\n\n"
SUB_SECTION_TEMPLATE = "### {0}\n\n"

ENTRY_LINK_EMPTY_TEMPLATE = "- {link}\n"
ENTRY_LINK_TEMPLATE = "- [{0}]({1})\n"

FROM_TEMPLATE = "* From {0} by {1}:\n"
FILE_TEMPLATE = "\t- [`{0}`]({0})\n"


def _build_header(template, entry, output_file):
    if TITLE_ATTRIBUTE_NAME in entry:
        title = entry[TITLE_ATTRIBUTE_NAME]
        url = ""

        if URL_ATTRIBUTE_NAME in entry:
            url = entry[URL_ATTRIBUTE_NAME]

        if len(url) != 0:
            title = LINK_TEMPLATE.format(url, title)

        output_file.write(template.format(title))


def _build_element(data, output_file):
    if LINK_ATTRIBUTE_NAME in data:
        output_file.write(ENTRY_LINK_EMPTY_TEMPLATE.format_map(data))
    elif TEXT_ATTRIBUTE_NAME in data:
        # Just use the plain text data.
        output_file.write(data[TEXT_ATTRIBUTE_NAME] + "\n\n")
    elif SOURCE_ATTRIBUTE_NAME in data:
        path = data[SOURCE_ATTRIBUTE_NAME]
        try:
            with open(path, "rt", encoding="utf-8") as f:
                output_file.write(f.read())
                output_file.write("\n")
        except Exception:
            return
    elif FILES_ATTRIBUTE_NAME in data:
        # Should have at least from and author.
        if FROM_ATTRIBUTE_NAME not in data or AUTHOR_ATTRIBUTE_NAME not in data:
            return

        data_from = data[FROM_ATTRIBUTE_NAME]
        data_author = data[AUTHOR_ATTRIBUTE_NAME]

        if FROM_URL_ATTRIBUTE_NAME in data:
            url = data[FROM_URL_ATTRIBUTE_NAME]
            data_from = LINK_TEMPLATE.format(url, data_from)

        if AUTHOR_URL_ATTRIBUTE_NAME in data:
            url = data[AUTHOR_URL_ATTRIBUTE_NAME]
            data_author = LINK_TEMPLATE.format(url, data_author)

        entry = FROM_TEMPLATE.format(data_from, data_author)

        output_file.write(entry)

        body = ""
        for file in data[FILES_ATTRIBUTE_NAME]:
            body += FILE_TEMPLATE.format(file)

        output_file.write(body)
        output_file.write("\n")
    else:
        print("Rest: ", data)


def _build_sub_section(data, output_file):
    for entry in data:
        if type(entry) is not dict:
            # Malformed, skip.
            continue

        if ELEMENTS_ATTRIBUTE_NAME in entry:
            _build_header(SUB_SECTION_TEMPLATE, entry, output_file)
            for element in entry[ELEMENTS_ATTRIBUTE_NAME]:
                _build_element(element, output_file)
        else:
            _build_element(entry, output_file)


def _build_section(data, output_file):
    for entry in data:
        if type(entry) is not dict:
            # Malformed, skip.
            continue

        if ELEMENTS_ATTRIBUTE_NAME in entry:
            _build_header(SECTION_TEMPLATE, entry, output_file)
            _build_sub_section(entry[ELEMENTS_ATTRIBUTE_NAME], output_file)
        else:
            _build_element(entry, output_file)


def _build_super_sections(data, output_file):
    for entry in data:
        if type(entry) is not dict:
            # Malformed, skip.
            continue

        if ELEMENTS_ATTRIBUTE_NAME in entry:
            _build_header(SUPER_SECTION_TEMPLATE, entry, output_file)
            _build_section(entry[ELEMENTS_ATTRIBUTE_NAME], output_file)
        else:
            _build_element(entry, output_file)


license_path = sys.argv[1]
output_path = sys.argv[2]

license_data = None
output_data = ""

with open(license_path, "rt", encoding="utf-8") as f:
    license_data = json.load(f)


if type(license_data) is not list:
    print("Invalid usage of LicenseGenerator.py, data is not list.")
    sys.exit(1)

with open(output_path, "w", encoding="utf-8") as f:
    _build_super_sections(license_data, f)
