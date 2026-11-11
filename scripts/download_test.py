"""Phase 0 download test: can this machine fetch what the pipeline needs?

Run one probe per call so each shows up as its own step in CI:

    python scripts/download_test.py bhavcopy
    python scripts/download_test.py results
    python scripts/download_test.py bse

Each probe makes plain requests under an honest client name. If an exchange
refuses them, the probe fails and that refusal is the answer; the script does
not try to look like a browser.

Uses only the standard library so it runs before any dependency is installed.
"""

import io
import json
import sys
import urllib.error
import urllib.request
import zipfile
from datetime import date, timedelta

USER_AGENT = "radar-download-test/0.1"
TIMEOUT_SECONDS = 30

BHAVCOPY_URL = (
    "https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{day:%Y%m%d}_F_0000.csv.zip"
)
RESULTS_URL = (
    "https://www.nseindia.com/api/corporates-financial-results"
    "?index=equities&symbol=TITAN&period=Quarterly"
)
BSE_URL = "https://www.bseindia.com/"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def probe_bhavcopy() -> str:
    """Fetch the most recent daily price file from the last ten days."""
    today = date.today()
    last_error = "no day tried"
    for days_back in range(1, 11):
        day = today - timedelta(days=days_back)
        if day.weekday() >= 5:  # Saturday or Sunday
            continue
        try:
            body = fetch(BHAVCOPY_URL.format(day=day))
        except urllib.error.HTTPError as error:
            last_error = f"{day}: HTTP {error.code}"
            if error.code == 404:  # market holiday, or the file is not out yet
                continue
            raise
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            name = archive.namelist()[0]
            rows = archive.read(name).decode("utf-8").splitlines()
        if len(rows) < 1000:
            raise ValueError(f"{name} has only {len(rows)} lines")
        return f"{name}: {len(rows) - 1} rows"
    raise RuntimeError(f"no bhavcopy found in the last ten days ({last_error})")


def probe_results() -> str:
    """Fetch the list of Titan's quarterly results and check it has filing dates."""
    filings = json.loads(fetch(RESULTS_URL))
    if not isinstance(filings, list) or not filings:
        raise ValueError("expected a non-empty list of filings")
    dated = [f for f in filings if f.get("filingDate")]
    if not dated:
        raise ValueError("no filing carries a filingDate")
    return f"{len(filings)} filings, {len(dated)} with a filing date"


def probe_bse() -> str:
    """Check that BSE answers at all. Shareholding data comes from BSE."""
    body = fetch(BSE_URL)
    return f"home page returned {len(body)} bytes"


PROBES = {"bhavcopy": probe_bhavcopy, "results": probe_results, "bse": probe_bse}


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in PROBES:
        print(f"usage: download_test.py [{' | '.join(PROBES)}]")
        return 2
    name = argv[1]
    try:
        detail = PROBES[name]()
    except Exception as error:  # noqa: BLE001 - any failure is the result we report
        print(f"FAIL {name}: {type(error).__name__}: {error}")
        return 1
    print(f"OK   {name}: {detail}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
