from typing import Optional
import click
from users import UserFaker


@click.command()
@click.option("-n", default=1, help="Number of users to generate", type=int)
@click.option("-o", default="json", help="What to output (only json for now)")
@click.option("--seed", default=None, help="Seed for randomness", type=int)
def main(n: int, o: str, seed: Optional[int]):
    uf = UserFaker(seed=seed)
    users = uf.generate_many(n=n)
    if o.lower() == "json":
        print("[")
        print(",\n".join((x.toJSON() for x in users)))
        print("]")
    else:
        print("Only json supported right now")


if __name__ == "__main__":
    main()  # pylint: disable=E1120 #no args cuz stupid
