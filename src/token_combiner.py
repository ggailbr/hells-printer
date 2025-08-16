
import argparse
from pathlib import Path
import logging


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("token_folder", type=Path)
    args = parser.parse_args()

    tokens: list[Path] = list(args.token_folder.iterdir())
    tokens.sort()

    for token in tokens:
        if str(token).__contains__("_1.png") or str(token).__contains__("_2.png"):
            continue
        else:
            if tokens[-1] == token:
                continue
            tokens[-1].rename(str(token.absolute()).replace(".png","_2.png"))
            tokens.pop(-1)
            token.rename(str(token.absolute()).replace(".png","_1.png"))
