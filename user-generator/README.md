# Prerequisites

Run `pip install -r requirements.txt`

# Usage

```
Usage: main.py [OPTIONS]

Options:
  -n INTEGER      Number of users to generate
  -o TEXT         What to output (only json for now)
  --seed INTEGER  Seed for randomness
  --uzh-share FLOAT RANGE  Share (0-1) of generated people that are external
                           UZH students  [default: 0.15; 0<=x<=1]
  --help          Show this message and exit.
  ```

(all are optional, n defaults to 1, o defaults to json, seed defaults to no seed)

## What gets generated

- **ETH students**: VSETH members are put into the group of their Fachverein
  (`vseth-11xx-<fv>`, see `users/data/fv.csv`; VIS members additionally get
  `vseth-1601-regular-vis`). The matching group files live in
  `global-fake-data/groups`.
- **External UZH students** (`--uzh-share`): `firstname.lastname@uzh.ch`,
  `...@uzh.ch` edu-person id, no ETH study info, not VSETH members and no Legi
  (advant/kaba).
- **Extraordinary VIS members**: 40% of UZH people and 10% of members of other
  Fachvereine are in `vseth-1602-fvextra-vis` (plus `vseth-1116-vis`).
