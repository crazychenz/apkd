# Source Maintenance Targets

bundle DURATION="":
    ./scripts/create-bundle.sh {{DURATION}}

builddevpkgs TAG="":
    ./scripts/build-dev-pkgs.sh {{TAG}}

buildpkgs TAG="":
    ./scripts/build-pkgs.sh {{TAG}}

pytests *args:
    ./scripts/pytests.sh {{args}}

builddocs:
    ./docs/builders/api/build-docs.sh
    ./docs/builders/pandoc/build-docs.sh
    ./docs/builders/docusaurus/build-docs.sh