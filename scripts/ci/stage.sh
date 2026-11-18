#!/usr/bin/env bash
# Prepara el árbol para empaquetar un release:
#   1. Copia los binarios nativos recién compilados a la carpeta runtimes/ de cada SDK
#      (reemplazando los que estén versionados en git).
#   2. Estampa la versión del release en todos los manifiestos.
#
# Uso: scripts/ci/stage.sh <version> [carpeta-nativos]
#   <version>         ej. 2.1.0 o 2.2.0-beta.1
#   [carpeta-nativos] carpeta con <rid>/native/<archivo> (por defecto: natives)
set -euo pipefail

VERSION="${1:?Uso: stage.sh <version> [carpeta-nativos]}"
NATIVE_DIR="${2:-natives}"

# Pre-releases limitados a alpha/beta/rc: es lo que entienden a la vez SemVer (npm, NuGet,
# Cargo, Maven) y PEP 440 (PyPI normaliza 2.2.0-beta.1 -> 2.2.0b1). Algo como -test o -preview
# rompería el build de Python.
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-(alpha|beta|rc)(\.?[0-9]+)?)?$ ]]; then
  echo "::error::Versión inválida '$VERSION' (se esperaba X.Y.Z o X.Y.Z-alpha|beta|rc[.N])" >&2
  exit 1
fi

NATIVE_DIR="$(cd "$NATIVE_DIR" && pwd)"
cd "$(dirname "${BASH_SOURCE[0]}")/../.."   # raíz del repo

# ---------------------------------------------------------------------------
# 1. Binarios nativos
# ---------------------------------------------------------------------------
if ! find "$NATIVE_DIR" -type f -path '*/native/*' | grep -q .; then
  echo "::error::No hay binarios en $NATIVE_DIR/<rid>/native/" >&2
  exit 1
fi

RUNTIME_DIRS=(
  sdk/csharp/ReportForge/runtimes
  sdk/typescript/runtimes
  sdk/python/reportforge/runtimes
  sdk/php/runtimes
  sdk/java/src/main/resources/runtimes
)
for dir in "${RUNTIME_DIRS[@]}"; do
  rm -rf "$dir"
  mkdir -p "$dir"
  cp -R "$NATIVE_DIR"/. "$dir"/
  echo "runtimes -> $dir"
done

# ---------------------------------------------------------------------------
# 2. Versiones (solo la primera coincidencia de cada archivo = versión del proyecto)
# ---------------------------------------------------------------------------
stamp() { # archivo  regex-sed  reemplazo
  local file="$1" pattern="$2" replacement="$3"
  sed -i -E "0,/${pattern}/s//${replacement}/" "$file"
  grep -qF "$(printf '%s' "$replacement" | sed -E 's/\\//g')" "$file" \
    || { echo "::error::No se pudo estampar la versión en $file" >&2; exit 1; }
  echo "version $VERSION -> $file"
}

stamp Cargo.toml                                '^version = "[^"]*"'          "version = \"$VERSION\""
stamp sdk/csharp/ReportForge/ReportForge.csproj '<Version>[^<]*<\/Version>'   "<Version>$VERSION<\/Version>"
stamp sdk/typescript/package.json               '"version": "[^"]*"'          "\"version\": \"$VERSION\""
stamp sdk/python/pyproject.toml                 '^version = "[^"]*"'          "version = \"$VERSION\""
stamp sdk/python/setup.py                       'version="[^"]*"'             "version=\"$VERSION\""
stamp sdk/java/pom.xml                          '<version>[^<]*<\/version>'   "<version>$VERSION<\/version>"
# PHP: Packagist toma la versión del tag git; el campo "version" en composer.json
# se elimina en el job del espejo para que no haya conflicto.
