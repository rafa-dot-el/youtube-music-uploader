{
  description = "Youtube Music Uploader";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        inherit (poetry2nix.legacyPackages.${system}) mkPoetryApplication;
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python310;
      in {
        packages = {
          myapp = mkPoetryApplication {
            projectDir = self;
            inherit python;
            nativeBuildInputs = with pkgs; [ pkg-config ];
            overrides = pkgs.poetry2nix.overrides.withDefaults (self: super:
              let
                # workaround https://github.com/nix-community/poetry2nix/issues/568
                addBuildInputs = name: buildInputs:
                  super.${name}.overridePythonAttrs (old: {
                    buildInputs = (builtins.map (x: super.${x}) buildInputs)
                      ++ (old.buildInputs or [ ]);
                  });
                mkOverrides = pkgs.lib.attrsets.mapAttrs
                  (name: value: addBuildInputs name value);
              in mkOverrides {
                iniconfig = [ "setuptools" "hatchling" "hatch-vcs" ];
              });
          };
          default = self.packages.${system}.myapp;
        };

        devShells.default = pkgs.mkShell rec {

          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath packages;
          buildInputs = with pkgs; [ zlib stdenv.cc.cc.lib pkg-config ];
          packages = with pkgs; [
            poetry2nix.packages.${system}.poetry
            pkg-config
          ];
        };
      });
}
