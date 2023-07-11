import re
import shutil
import subprocess
import tempfile
import webbrowser


class Cosign:
    bin: str

    def __init__(self):
        self.bin = shutil.which("cosign")
        if self.bin is None:
            raise RuntimeError("cosign not found")

    def sign(self, hash: str) -> str:
        with tempfile.NamedTemporaryFile() as f:
            proc = subprocess.Popen(
                args=[self.bin, "sign-blob", "-", "-y", "--bundle", f.name],
                text=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            proc.stdin.write(hash)
            proc.stdin.close()
            proc.stdin = None

            resp = ""
            while not (match := re.search(r"https://.*\n", resp, re.MULTILINE)):
                resp += proc.stdout.read(1)

            webbrowser.open(match.group(0))
            proc.communicate(timeout=60)
            return f.read().decode("utf-8")

    def verify(self, hash: str, bundle: str, issuer=".*", identity=".*"):
        try:
            with tempfile.NamedTemporaryFile() as f:
                f.write(bundle.encode("utf-8"))
                f.flush()
                subprocess.run(
                    args=[
                        self.bin,
                        "verify-blob",
                        "-",
                        "--bundle",
                        f.name,
                        "--certificate-identity-regexp",
                        identity,
                        "--certificate-oidc-issuer-regexp",
                        issuer,
                    ],
                    check=True,
                    input=hash.encode("utf-8"),
                )
            return True
        except subprocess.CalledProcessError:
            return False
