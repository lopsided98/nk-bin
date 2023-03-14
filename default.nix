{ lib, nixShell ? false, buildPythonApplication, mypy, autopep8, pylint, rope }:

buildPythonApplication {
  pname = "nk-bin";
  version = "0.1.1";
  format = "setuptools";

  # lib.inNixShell can't be used here because it will return a false positive
  # if this package is pulled into a shell
  src = if nixShell then null else lib.cleanSourceWith {
    filter = name: type: let baseName = baseNameOf (toString name); in !(
      # Filter out mypy cache
      (baseName == ".mypy_cache" && type == "directory")
    );
    src = lib.cleanSource ./.;
  };

  # Devlopment dependencies
  nativeBuildInputs = lib.optionals nixShell [ mypy autopep8 pylint rope ];

  meta = with lib; {
    description = "Generate WinCE boot images to run custom code";
    license = licenses.gpl3Plus;
    maintainers = with maintainers; [ lopsided98 ];
  };
}
