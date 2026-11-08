"""Export the Cloudflare Bulk Redirect list or verify the live HTTP status and target."""
import csv
import json
import sys
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from build import ROOT, SITE

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def main():
    redirects = json.loads((ROOT / "content/redirects.json").read_text(encoding="utf-8"))
    mappings = [(SITE + variant, SITE + target) for old, target in redirects.items()
                for variant in (old, old.rstrip("/"), old + "index.html")]
    if "--verify" not in sys.argv:
        csv.writer(sys.stdout, lineterminator="\n").writerows(
            (source, target, 301, "TRUE", "FALSE", "FALSE", "FALSE") for source, target in mappings
        )
        return
    opener = build_opener(NoRedirect())
    failed = False
    for source, target in mappings:
        try:
            with opener.open(Request(source, method="HEAD"), timeout=15) as response:
                status, location = response.status, response.headers.get("Location")
        except HTTPError as error:
            status, location = error.code, error.headers.get("Location")
        correct = (status, location) == (301, target)
        if correct:
            with opener.open(Request(target, method="HEAD"), timeout=15) as destination:
                correct = destination.status == 200
        print(f"{'PASS' if correct else 'FAIL'} {source} → {status} {location or '(no Location)'}")
        failed |= not correct
    sys.exit(int(failed))

if __name__ == "__main__":
    main()
