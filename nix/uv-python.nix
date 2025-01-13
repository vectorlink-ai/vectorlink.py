{pyproject-nix, pyproject-build-systems, cudaPackages, lib, workspace, python3, callPackage}:
let overlay = workspace.mkPyprojectOverlay {
      sourcePreference = "wheel";
    };
    pyprojectOverrides = final: prev: {
      pybars3 = prev.pybars3.overrideAttrs (p:{
        nativeBuildInputs = p.nativeBuildInputs ++ [final.setuptools];
      });
      pymeta3 = prev.pymeta3.overrideAttrs (p:{
        nativeBuildInputs = p.nativeBuildInputs ++ [final.setuptools];
      });
    };
in
(callPackage pyproject-nix.build.packages {
  python = python3;
}).overrideScope (
  lib.composeManyExtensions [
    pyproject-build-systems.overlays.default
    overlay
    pyprojectOverrides
  ]
)
