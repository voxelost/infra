import sqlite3


def get_cookies_for_domain(domain: str):
    con = sqlite3.connect(
        # "/Users/voxelost/Library/Application Support/Firefox/Profiles/g92hix35.default-release-2/cookies.sqlite"
        "src/jackett/cookies.sqlite"
    )
    cur = con.cursor()
    res = cur.execute(f"SELECT * FROM moz_cookies WHERE host='{domain}'")

    getidx = lambda key: [col[0] for col in res.description].index(key)

    name_idx = getidx("name")
    value_idx = getidx("value")

    return {cookie[name_idx]: cookie[value_idx] for cookie in res.fetchall()}
