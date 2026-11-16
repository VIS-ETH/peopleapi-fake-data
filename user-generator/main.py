from typing import Optional
import click
from users import UserFaker
from users.generate import UZH_SHARE


@click.command()
@click.option("-n", default=1, help="Number of users to generate", type=int)
@click.option("-o", default="json", help="What to output (only json for now)")
@click.option("--seed", default=None, help="Seed for randomness", type=int)
@click.option(
    "--uzh-share",
    default=UZH_SHARE,
    show_default=True,
    help="Share (0-1) of generated people that are external UZH students",
    type=click.FloatRange(0, 1),
)
def main(n: int, o: str, seed: Optional[int], uzh_share: float):
    uf = UserFaker(seed=seed, uzh_share=uzh_share)
    users = uf.generate_many(n=n)
    if o.lower() == "json":
        print("[")
        print(",\n".join((x.toJSON() for x in users)))
        print("]")
    else:
        print("Only json supported right now")


if __name__ == "__main__":
    main()  # pylint: disable=E1120 #no args cuz stupid
