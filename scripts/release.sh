#!/bin/bash

# Script to build, publish, and tag a release for cased-piglet.

set -e

# Check if a version argument is provided.
if [ -z "$1" ]; then
  echo "Error: No version specified."
  echo "Usage: $0 <version>"
  echo "Example: $0 0.1.0"
  exit 1
fi

VERSION=$1
TAG_NAME="v${VERSION}"
PYPROJECT_TOML="pyproject.toml"

# --- Pre-flight checks ---

# 1. Check if pyproject.toml exists
if [ ! -f "${PYPROJECT_TOML}" ]; then
    echo "Error: ${PYPROJECT_TOML} not found in the current directory."
    exit 1
fi

# 2. Check if version in pyproject.toml matches the provided version
PYPROJECT_VERSION=$(sed -n 's/^version[[:space:]]*=[[:space:]]*\"\([^"]*\)\".*/\1/p' "${PYPROJECT_TOML}")

if [ "${PYPROJECT_VERSION}" != "${VERSION}" ]; then
    echo "Error: Version mismatch!"
    echo "  Provided version: ${VERSION}"
    echo "  Version in ${PYPROJECT_TOML}: ${PYPROJECT_VERSION}"
    echo "Please update ${PYPROJECT_TOML} to version = \"${VERSION}\" before releasing."
    exit 1
fi

# 3. Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "Error: You have uncommitted changes."
    echo "Please commit or stash all changes before tagging a release."
    exit 1
fi

# 4. Check if working branch is main/master
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "${CURRENT_BRANCH}" != "main" && "${CURRENT_BRANCH}" != "master" ]]; then
    echo "Warning: You are not on the main/master branch (current: ${CURRENT_BRANCH})."
    read -p "Continue anyway? (y/N): " confirm_branch
    if [[ "$confirm_branch" != [yY] ]]; then
        echo "Aborted by user."
        exit 1
    fi
fi

# 5. Check for required environment variables for PyPI upload
if [ -z "${TWINE_USERNAME}" ] || [ -z "${TWINE_PASSWORD}" ]; then
  echo "Error: TWINE_USERNAME and/or TWINE_PASSWORD environment variables are not set."
  echo "Please set them before running this script:"
  echo "  export TWINE_USERNAME=__token__"
  echo "  export TWINE_PASSWORD='your-pypi-api-token'"
  exit 1
fi

# 6. Check if build and twine are installed
echo "Checking for required build tools..."
if ! uv tool run --from build python -c "print('build ok')" &> /dev/null; then
    echo "Installing build tools..."
fi

echo ""
echo "Release pre-flight checks passed for version ${VERSION}."
read -p "Proceed with build, PyPI publish, and git tagging? (y/N): " confirm_proceed
if [[ "$confirm_proceed" != [yY] ]]; then
    echo "Aborted by user."
    exit 1
fi

# --- Build Package ---
echo ""
echo "Building package..."
rm -rf dist/

uv build

# --- Publish to PyPI ---
echo ""
echo "Publishing package to PyPI..."
uv tool run twine upload dist/*

# --- Tagging and Pushing Git Tag ---
echo ""
echo "Creating git tag '${TAG_NAME}'..."
git tag "${TAG_NAME}"

echo "Pushing git tag '${TAG_NAME}' to origin..."
git push origin "${TAG_NAME}"

# --- (Optional) Create GitHub Release ---
if command -v gh &> /dev/null; then
    echo ""
    read -p "Create a GitHub Release for tag ${TAG_NAME}? (y/N): " confirm_gh_release
    if [[ "$confirm_gh_release" == [yY] ]]; then
        echo "Creating GitHub Release for ${TAG_NAME}..."
        if gh release create "${TAG_NAME}" --title "Release ${VERSION}" --generate-notes; then
            echo "Successfully created GitHub Release for ${TAG_NAME}."
        else
            echo "Warning: Failed to create GitHub Release."
            echo "Please create the release manually on GitHub."
        fi
    fi
fi

echo ""
echo "Done! Version ${VERSION} released successfully."

exit 0
