{
  description = "Convert eBooks to audiobooks with chapters and metadata";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { self, nixpkgs }:
    let
      inherit (nixpkgs) lib;
      # the platforms of nix/package.nix: calibre and buildFHSEnv are Linux only
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forAllSystems = f: lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
      version = lib.fileContents ./VERSION.txt;
    in
    {
      packages = forAllSystems (
        pkgs:
        let
          # nix/package.nix is the nixpkgs package, which fetches its release tag: built here from this
          # checkout, at the version of VERSION.txt
          ebook2audiobook = pkgs.callPackage ./nix/package.nix {
            fetchFromGitHub = _: self;
            buildFHSEnv = args: pkgs.buildFHSEnv (args // { inherit version; });
            python3Packages = pkgs.python3Packages // {
              buildPythonApplication =
                args: pkgs.python3Packages.buildPythonApplication (args // { inherit version; });
            };
          };
        in
        {
          inherit ebook2audiobook;
          default = ebook2audiobook;
        }
      );
    };
}
