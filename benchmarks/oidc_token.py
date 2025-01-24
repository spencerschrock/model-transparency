# Copyright 2024 The Sigstore Authors
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

"""Grab a token."""

from base64 import b64decode
from datetime import datetime
from datetime import timedelta
import json
import os
import subprocess
from tempfile import TemporaryDirectory
import time
from typing import Optional


_MIN_VALIDITY = timedelta(minutes=1)
_MAX_RETRY_TIME = timedelta(minutes=5)
_RETRY_SLEEP_SECS = 30


class DangerousPublicOIDCBeacon:
    """Fetches and validates tokens from Sigstore's testing beacon repo."""

    def __init__(self):
        self._token = ""

    def _fetch(self) -> None:
        # the git approach is apparently fresher than https://raw.githubusercontent.com
        # https://github.com/sigstore-conformance/extremely-dangerous-public-oidc-beacon/issues/17
        git_url = "https://github.com/sigstore-conformance/extremely-dangerous-public-oidc-beacon.git"
        with TemporaryDirectory() as tmpdir:
            base_cmd = [
                "git",
                "clone",
                "--quiet",
                "--single-branch",
                "--branch=current-token",
                "--depth=1",
            ]
            subprocess.run(base_cmd + [git_url, tmpdir], check=True)
            token_path = os.path.join(tmpdir, "oidc-token.txt")
            with open(token_path) as f:
                self._token = f.read().rstrip()

    def _expiration(self) -> datetime:
        payload = self._token.split(".")[1]
        payload += "=" * (4 - len(payload) % 4)
        payload_json = json.loads(b64decode(payload))
        return datetime.fromtimestamp(payload_json["exp"])

    def token(self) -> Optional[str]:
        start = datetime.now()
        while True:
            now = datetime.now()
            deadline = now + _MIN_VALIDITY
            self._fetch()
            exp = self._expiration()
            if deadline < exp:
                return self._token
            if now > start + _MAX_RETRY_TIME:
                break
            time.sleep(_RETRY_SLEEP_SECS)
        return None
