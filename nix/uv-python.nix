{pyproject-nix, pyproject-build-systems, cudaPackages, lib, workspace, python3, callPackage}:
let overlay = workspace.mkPyprojectOverlay {
      sourcePreference = "wheel";
    };
    pyprojectOverrides = final: prev: {
      # overrides here
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
