# Copyright 2025 The Sigstore Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Script for generating paper files."""

import argparse
import pathlib
import time
from typing import Final

import generate
import serialize


B: Final[int] = 1
KB: Final[int] = 1024 * B
MB: Final[int] = 1024 * KB
GB: Final[int] = 1024 * MB
TB: Final[int] = 1024 * GB


def build_parser() -> argparse.ArgumentParser:
    """Builds the command line parser for the chunk experiment."""
    parser = argparse.ArgumentParser(description="paper benchmark data")

    parser.add_argument("path", help="temporary file to use")

    parser.add_argument(
        "--repeat",
        help="how many times to repeat serializing each model",
        type=int,
        default=6,
    )

    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()

    for scale in [B, KB, MB, GB, TB]:
        for base in [1, 2, 5, 10, 20, 50, 100, 200, 500]:
            size = base * scale
            if size > TB:
                break
            gen_args = generate.build_parser().parse_args(
                ["file", f"--root={args.path}", str(size)]
            )
            generate.generate_file(gen_args)

            ser_args = serialize.build_parser().parse_args(
                [
                    args.path,
                    "--chunk=8388608",
                    "--use_shards",
                    "--shard=1073741824",
                    "--single_digest",
                    "--hash_method=sha256",
                ]
            )

            times = []
            for _ in range(args.repeat):
                st = time.time()
                payload = serialize.run(ser_args)
                en = time.time()
                times.append(f"{en-st:0.4f}")
            print(f"{size},{','.join(times)}")

            pathlib.Path(args.path).unlink()
