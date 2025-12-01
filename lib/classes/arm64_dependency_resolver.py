#!/usr/bin/env python3
import json
import re
import sys
import subprocess
import urllib.request
import os


class Arm64DependencyResolver:

    AARCH64_PATTERNS = [
        "aarch64",
        "arm64",
        r"manylinux.*aarch64"
    ]

    def __init__(
        self,
        requirements_file="requirements.txt",
        report_file="pip_deps_report.json"
    ):
        self.requirements_file = requirements_file
        self.report_file = report_file

    def run_cmd(self, cmd: list) -> str:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if p.returncode != 0:
            print(f"ERROR running: {' '.join(cmd)}\n{p.stderr}", file=sys.stderr)
            self.cleanup()
            sys.exit(1)
        return p.stdout

    def cleanup(self):
        """Delete temporary report file."""
        if os.path.exists(self.report_file):
            try:
                os.remove(self.report_file)
                print(f"🧹 Cleanup: deleted {self.report_file}")
            except Exception as e:
                print(f"⚠️ Could not delete {self.report_file}: {e}")

    def create_dependency_report(self):
        print("🔍 Generating pip dependency report...")
        self.run_cmd([
            sys.executable, "-m", "pip", "install",
            "--dry-run",
            "--report", self.report_file,
            "-r", self.requirements_file
        ])
        print("✔ Dependency report created.")

    def load_dependency_tree(self) -> dict:
        if not os.path.exists(self.report_file):
            print(f"ERROR: Dependency report {self.report_file} not found.")
            sys.exit(1)
        with open(self.report_file, "r") as f:
            report = json.load(f)
        deps = {}
        for entry in report.get("install", []):
            meta = entry.get("metadata", {})
            name = meta.get("name")
            version = meta.get("version")
            if name and version:
                deps[name] = version
        return deps

    def has_aarch64_wheel(self, pkg: str, version: str) -> bool:
        try:
            url = f"https://pypi.org/pypi/{pkg}/json"
            data = json.loads(urllib.request.urlopen(url).read())
            releases = data.get("releases", {}).get(version, [])
            for f in releases:
                fname = f.get("filename", "").lower()
                for pat in self.AARCH64_PATTERNS:
                    if re.search(pat, fname):
                        return True
            return False
        except Exception:
            return False

    def install_source_build(self, pkg: str, version: str):
        full_spec = f"{pkg}=={version}"
        print(f"⚙️  Building from source: {full_spec}")
        subprocess.check_call([
            sys.executable,
            "-m", "pip",
            "install",
            "--no-binary", pkg,
            full_spec
        ])

    def resolve(self):
        try:
            if not os.path.exists(self.requirements_file):
                print(f"❌ {self.requirements_file} not found.")
                sys.exit(1)

            self.create_dependency_report()
            deps = self.load_dependency_tree()

            print("\n🔍 Checking ARM64 wheel availability...\n")

            needs_source = []

            for pkg, version in deps.items():
                print(f"{pkg}=={version} ... ", end="")
                if self.has_aarch64_wheel(pkg, version):
                    print("✔ ARM64 wheel found")
                else:
                    print("❌ NO ARM64 wheel")
                    needs_source.append((pkg, version))

            if not needs_source:
                print("\n🎉 All packages have ARM64 wheels. Nothing to compile.")
                return []

            print(f"\n⚠️  {len(needs_source)} packages require source build:")
            for pkg, ver in needs_source:
                print(f" - {pkg}=={ver}")

            print("\n🚀 Starting source builds...\n")

            for pkg, version in needs_source:
                try:
                    self.install_source_build(pkg, version)
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to build {pkg}=={version}: {e}")
                    self.cleanup()
                    sys.exit(1)

            print("\n✔ All required ARM64 source builds completed.\n")
            return needs_source

        finally:
            # ALWAYS delete the report file after work
            self.cleanup()


if __name__ == "__main__":
    resolver = Arm64DependencyResolver()
    resolver.resolve()