import os

import requests_cache

url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"


def get_api_key():
    """
    Get the NCBI API key.
    :return:
    """
    return os.environ.get("NCBI_API_KEY", None)


def pmid_to_pmc(pmid, api_key=None):
    """
    Convert a PMID to a PMCID.

    >>> pmid_to_pmc("37389415")
    'PMC10336030'

    :param pmid:
    :param api_key:
    :return:
    """
    session = requests_cache.CachedSession("eutils_cache")
    if api_key is None:
        api_key = get_api_key()

    params = {"dbfrom": "pubmed", "db": "pmc", "id": pmid, "api_key": api_key, "retmode": "json"}

    response = session.get(url, params=params)
    data = response.json()

    try:
        pmc_id = data["linksets"][0]["linksetdbs"][0]["links"][0]
        return f"PMC{pmc_id}"
    except (IndexError, KeyError):
        return None
