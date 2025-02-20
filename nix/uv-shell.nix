{workspace, pythonSet, mkShell, uv, lib, cudaPackages, cudatoolkit, gdb}:
let editableOverlay = workspace.mkEditablePyprojectOverlay {
      # Use environment variable
      root = "$REPO_ROOT";
    };
    editablePythonSet = pythonSet.overrideScope (
      lib.composeManyExtensions [
        editableOverlay
        (final:  prev: {
          vectorlink = prev.vectorlink.overrideAttrs (old: {
            nativeBuildInputs =
              old.nativeBuildInputs
              ++ final.resolveBuildSystem {
                editables = [ ];
              };
          });
        })
      ]);
    virtualenv = editablePythonSet.mkVirtualEnv "vectorlink-py-env" workspace.deps.all; in
mkShell {
  packages = [
    virtualenv
    uv
  ];
  env = {
    UV_NO_SYNC = 1;
  };
  shellHook = ''
    # Undo dependency propagation by nixpkgs.
    unset PYTHONPATH
    # Get repository root using git. This is expanded at runtime by the editable `.pth` machinery.
    export REPO_ROOT=$(git rev-parse --show-toplevel)
    export CUDA_HOME=${cudatoolkit}
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${cudaPackages.cuda_nvcc}/nvvm/lib64:${lib.makeLibraryPath [cudatoolkit]}"
  '';
}

