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
import time

from oidc_token import DangerousPublicOIDCBeacon
import serialize

from model_signing.signing import in_toto
from model_signing.signing import sign_sigstore as sigstore


def build_parser() -> argparse.ArgumentParser:
    """Builds the command line parser for the chunk experiment."""
    parser = argparse.ArgumentParser(description="paper benchmark data")

    parser.add_argument("path", help="path to model")

    parser.add_argument(
        "--repeat",
        help="how many times to repeat each model",
        type=int,
        default=6,
    )

    parser.add_argument(
        "--sign",
        help="whether to time sigstore signing time",
        action="store_true",
    )

    return parser


if __name__ == "__main__":
    paper_args = build_parser().parse_args()

    args = serialize.build_parser().parse_args(
        [
            paper_args.path,
            "--chunk=8388608",
            "--use_shards",
            "--shard=1073741824",
            "--single_digest",
            "--hash_method=sha256",
        ]
    )

    print(paper_args.path)
    beacon = DangerousPublicOIDCBeacon()
    for _ in range(paper_args.repeat):
        st = time.time()
        payload = serialize.run(args)
        en = time.time()
        hash = en - st

        if not paper_args.sign:
            print(f"hash: {hash:0.4f}")
            continue

        assert isinstance(payload, in_toto.IntotoPayload)

        token = beacon.token()
        signer = sigstore.SigstoreDSSESigner(
            use_staging=True, identity_token=token
        )
        st = time.time()
        sig = signer.sign(payload)
        en = time.time()
        sign = en - st
        total = hash + sign
        print(f"hash: {hash:0.4f} sign: {sign:0.4f} total: {total:0.4f}")
