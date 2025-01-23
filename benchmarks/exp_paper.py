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


"""Script for running paper benchmarks."""

import argparse
import timeit

import serialize


def build_parser() -> argparse.ArgumentParser:
    """Builds the command line parser for the chunk experiment."""
    parser = argparse.ArgumentParser(
        description="paper benchmark data"
    )

    parser.add_argument("path", help="path to model")

    parser.add_argument(
        "--repeat",
        help="how many times to repeat each model",
        type=int,
        default=5,
    )

    return parser

if __name__ == "__main__":
    paper_args = build_parser().parse_args()

    args = serialize.build_parser().parse_args(
        [paper_args.path, "--chunk=8388608", "--use_shards", "--shard=1073741824"]
    )
    times = timeit.repeat(
        lambda args=args: serialize.run(args),
        number=1,
        repeat=paper_args.repeat,
    )
    print(paper_args.path, times)
