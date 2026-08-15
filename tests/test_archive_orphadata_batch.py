from __future__ import annotations

import pytest

from scripts.archive_orphadata_batch import discover_file_urls


def test_discover_file_urls_keeps_exact_official_files_in_page_order():
    html = """
    <a href="https://www.orphadata.com/data/xml/en_product1.xml">XML</a>
    <a href="https://www.orphadata.com/data/json/en_product1.json.tar.gz">JSON</a>
    <a href="https://www.orphadata.com/data/xml/en_product1.xml">duplicate</a>
    """
    assert discover_file_urls(html, "https://sciences.orphadata.com/alignments/") == [
        "https://www.orphadata.com/data/xml/en_product1.xml",
        "https://www.orphadata.com/data/json/en_product1.json.tar.gz",
    ]


def test_discover_file_urls_rejects_non_https_and_other_hosts():
    html = """
    <a href="http://www.orphadata.com/data/xml/en_product1.xml">HTTP</a>
    <a href="https://example.org/en_product1.xml">other host</a>
    """
    assert not discover_file_urls(html, "https://sciences.orphadata.com/alignments/")


@pytest.mark.parametrize("suffix", ["exe", "html", "pdf"])
def test_discover_file_urls_rejects_non_data_suffixes(suffix):
    html = f'<a href="https://www.orphadata.com/data/en_product1.{suffix}">file</a>'
    assert not discover_file_urls(html, "https://sciences.orphadata.com/alignments/")
