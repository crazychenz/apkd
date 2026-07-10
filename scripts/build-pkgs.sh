#!/usr/bin/env bash

export PROJ_PATH=$(realpath $(dirname $0)/..)
cd ${PROJ_PATH}

# Note: VERSION is git-ignored (not revision controlled)
if [ -z "$1" ]; then
  VERSION="0.0.0.dev0"
else
  VERSION=$1
fi

echo "Adding VERSION files."
for pkg in $(find packages -mindepth 1 -maxdepth 1 -name "*" -printf '%f\n'); do
  [ ! -e "packages/$pkg/.yannt-build" ] && continue
  echo "$VERSION" > "packages/$pkg/VERSION"
done

# Rebuild all packages
echo "Building packages."
mkdir -p outputs/dist
for pkg in $(find packages -mindepth 1 -maxdepth 1 -name "*" -printf '%f\n'); do
  [ ! -e "packages/$pkg/.yannt-build" ] && continue
  (pushd "packages/$pkg" \
    && python -m build --no-isolation --outdir ${PROJ_PATH}/outputs/dist \
    && python -m build --no-isolation --sdist --outdir ${PROJ_PATH}/outputs/dist)
done

echo "Building publish and requirements scripts."
pushd outputs/dist

echo "" > config-$VERSION.sh
echo "CERT_ARGS=\"-k --cert PATH_TO_CLIENT_CERT_HERE\"" >> config-$VERSION.sh
echo "GL_USER=USERNAME" >> config-$VERSION.sh
echo "GL_TOKEN=TOKEN" >> config-$VERSION.sh
echo "ENDPT=https://gitlab/api/v4/projects/group%2Fproject/packages" >> config-$VERSION.sh
echo "" >> config-$VERSION.sh

echo "#!/bin/sh" > publish-pypi-$VERSION.sh
echo "# Load configuration" >> publish-pypi-$VERSION.sh
echo ". ./config-$VERSION.sh" >> publish-pypi-$VERSION.sh
echo "" >> publish-pypi-$VERSION.sh
chmod +x publish-pypi-$VERSION.sh

# Copy our template to other generated files.
cp publish-pypi-$VERSION.sh publish-generic-$VERSION.sh
cp publish-pypi-$VERSION.sh gen-requirements-pypi-$VERSION.sh
cp publish-pypi-$VERSION.sh gen-requirements-generic-$VERSION.sh
cp publish-pypi-$VERSION.sh gen-requirements-sdist-$VERSION.sh
echo "" > requirements-wheels-$VERSION.txt
echo "" > requirements-sdist-$VERSION.txt

echo "Adding wheels to scripts."
shopt -s nullglob
for pkg in $(find . -maxdepth 1 -name "*-$VERSION-py3*" -printf '%f\n') ; do
  echo $pkg
  PKGMETADATA=$(unzip -p "$pkg" "*.dist-info/METADATA")
  PKGNAME=$(echo "$PKGMETADATA" | grep "^Name:" | cut -d: -f2 | xargs)
  PKGVERSION=$(echo "$PKGMETADATA" | grep "^Version:" | cut -d: -f2 | xargs)

  # do pypi wheels
  echo "echo \"Pushing to pypi: $pkg\"" >> publish-pypi-$VERSION.sh
  echo "curl \$CERT_ARGS --request POST \\" >> publish-pypi-$VERSION.sh
  echo "  --user \$GL_USER:\$GL_TOKEN \\" >> publish-pypi-$VERSION.sh
  echo "  --form \"content=@$pkg\" \\" >> publish-pypi-$VERSION.sh
  echo "  --form \"name=$PKGNAME\" \\" >> publish-pypi-$VERSION.sh
  echo "  --form \"version=$PKGVERSION\" \\" >> publish-pypi-$VERSION.sh
  echo "  \$ENDPT/pypi" >> publish-pypi-$VERSION.sh
  echo "echo \"\"" >> publish-pypi-$VERSION.sh
  echo "" >> publish-pypi-$VERSION.sh

  echo "echo \"\$ENDPT/simple/$PKGNAME/$pkg\" >> requirements-pypi-$VERSION.txt" >> gen-requirements-pypi-$VERSION.sh

  # do generic wheels
  echo "echo \"Pushing to generic: $pkg\"" >> publish-generic-$VERSION.sh
  echo "curl \$CERT_ARGS \\" >>  publish-generic-$VERSION.sh
  echo "  --header \"PRIVATE-TOKEN: \$GL_TOKEN\" \\" >>  publish-generic-$VERSION.sh
  echo "  --upload-file $pkg \\" >>  publish-generic-$VERSION.sh
  echo "  \"\$ENDPT/generic/$PKGNAME/$PKGVERSION/$pkg\"" >> publish-generic-$VERSION.sh
  echo "echo \"\"" >> publish-pypi-$VERSION.sh
  echo "" >>  publish-generic-$VERSION.sh

  echo "echo \"\$ENDPT/generic/$PKGNAME/$PKGVERSION/$pkg\" >> requirements-generic-$VERSION.txt" >> gen-requirements-generic-$VERSION.sh

  echo "$pkg" >> requirements-wheels-$VERSION.txt
done

echo "Adding sdist to scripts."
shopt -s nullglob
for pkg in $(find . -maxdepth 1 -name "*-$VERSION.tar.gz" -printf '%f\n') ; do
  #echo --------------------------------------------------------
  #echo $pkg
  PKGMETADATA=$(tar -xOzf $pkg --wildcards '*/PKG-INFO')
  PKGNAME=$(echo "$PKGMETADATA" | grep '^Name:' | head -1 | cut -d: -f2 | xargs)
  PKGVERSION=$(echo "$PKGMETADATA" | grep '^Version:' | head -1 | cut -d: -f2 | xargs)
  #echo PKGMETADATA: $PKGMETADATA
  #echo PKGNAME: $PKGNAME
  #echo PKGVERSION: $PKGVERSION
  #echo --------------------------------------------------------
  

  # do pypi sdists
  echo "echo \"Pushing to pypi: $pkg\"" >> publish-pypi-$VERSION.sh
  echo "curl \$CERT_ARGS --request POST \\" >> publish-pypi-$VERSION.sh
  echo "  --user \$GL_USER:\$GL_TOKEN \\" >> publish-pypi-$VERSION.sh
  echo "  --form \"content=@$pkg\" \\" >> publish-pypi-$VERSION.sh
  echo "  --form \"name=$PKGNAME\" \\" >> publish-pypi-$VERSION.sh
  echo "  --form \"version=$PKGVERSION\" \\" >> publish-pypi-$VERSION.sh
  echo "  \$ENDPT/pypi" >> publish-pypi-$VERSION.sh
  echo "echo \"\"" >> publish-pypi-$VERSION.sh
  echo "" >> publish-pypi-$VERSION.sh

  # do generic sdists
  echo "echo \"Pushing to generic: $pkg\"" >> publish-generic-$VERSION.sh
  echo "curl \$CERT_ARGS \\" >>  publish-generic-$VERSION.sh
  echo "  --header \"PRIVATE-TOKEN: \$GL_TOKEN\" \\" >>  publish-generic-$VERSION.sh
  echo "  --upload-file $pkg \\" >>  publish-generic-$VERSION.sh
  echo "  \"\$ENDPT/generic/$PKGNAME/$PKGVERSION/$pkg\"" >> publish-generic-$VERSION.sh
  echo "echo \"\"" >> publish-pypi-$VERSION.sh
  echo "" >>  publish-generic-$VERSION.sh

  echo "echo \"\$ENDPT/generic/$PKGNAME/$PKGVERSION/$pkg\" >> requirements-sdist-$VERSION.txt" >> gen-requirements-sdist-$VERSION.sh

  echo "$pkg" >> requirements-sdist-$VERSION.txt
done

# Build a minimal set of packages for offline deployments.
grep -vi naive requirements-wheels-$VERSION.txt | grep -v _hft > requirements-wise-wheels-$VERSION.txt
PIP_PKG_PATH=yannt-pip-pkgs-py$(python --version | awk '{print $2}')-$VERSION
mkdir -p $PIP_PKG_PATH
pip download -r requirements-wise-wheels-$VERSION.txt -d $PIP_PKG_PATH
cp requirements-wise-wheels-$VERSION.txt $PIP_PKG_PATH/requirements.txt
tar -czf $PIP_PKG_PATH.tar.gz $PIP_PKG_PATH

# pop out of outputs/dist
popd

echo "!! Ensure clean repo before tagging. !!"
echo
echo git tag v$VERSION
echo
echo git push origin v$VERSION
echo