#!/usr/bin/env bash
# Prepara el árbol para empaquetar un release:
#   1. Copia los binarios nativos recién compilados a la carpeta runtimes/ de cada SDK
#      (reemplazando los que estén versionados en git).
#   2. Estampa la versión del release en todos los manifiestos.
#
# Uso: scripts/ci/stage.sh <version> [carpeta-nativos]
#      scripts/ci/stage.sh --natives-only [carpeta-nativos]   (solo paso 1; desarrollo local)
#   <version>         ej. 1.0.0 o 1.1.0-beta.1
#   [carpeta-nativos] carpeta con <rid>/native/<archivo> (por defecto: natives)
set -euo pipefail

NATIVES_ONLY=false
if [[ "${1:-}" == --natives-only ]]; then NATIVES_ONLY=true; shift; set -- 0.0.0 "$@"; fi
VERSION="${1:?Uso: stage.sh <version> [carpeta-nativos]}"
NATIVE_DIR="${2:-natives}"

# Pre-releases limitados a alpha/beta/rc: es lo que entienden a la vez SemVer (npm, NuGet,
# Cargo, Maven) y PEP 440 (PyPI normaliza 1.1.0-beta.1 -> 1.1.0b1). Algo como -test o -preview
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
  sdk/csharp/FlowPdf/runtimes
  sdk/typescript/runtimes
  sdk/python/flowpdf/runtimes
  sdk/php/runtimes
  sdk/java/src/main/resources/runtimes
)
for dir in "${RUNTIME_DIRS[@]}"; do
  rm -rf "$dir"
  mkdir -p "$dir"
  cp -R "$NATIVE_DIR"/. "$dir"/
  echo "runtimes -> $dir"
done
$NATIVES_ONLY && exit 0

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
stamp sdk/csharp/FlowPdf/FlowPdf.csproj '<Version>[^<]*<\/Version>'   "<Version>$VERSION<\/Version>"
stamp sdk/typescript/package.json               '"version": "[^"]*"'          "\"version\": \"$VERSION\""
stamp sdk/python/pyproject.toml                 '^version = "[^"]*"'          "version = \"$VERSION\""
stamp sdk/python/setup.py                       'version="[^"]*"'             "version=\"$VERSION\""
stamp sdk/java/pom.xml                          '<version>[^<]*<\/version>'   "<version>$VERSION<\/version>"
# Versiones visibles en tiempo de ejecución (User-Agent de los clientes HTTP, __version__)
stamp sdk/python/flowpdf/__init__.py            '^__version__ = "[^"]*"'      "__version__ = \"$VERSION\""
stamp sdk/python/flowpdf/client.py              'FlowPDF-Python-SDK\/[0-9A-Za-z.-]*' "FlowPDF-Python-SDK\/$VERSION"
stamp sdk/java/src/main/java/io/github/codepro47rd/flowpdf/FlowPdfClient.java 'FlowPDF-Java-SDK\/[0-9A-Za-z.-]*' "FlowPDF-Java-SDK\/$VERSION"
stamp sdk/php/src/FlowPdfClient.php             'FlowPDF-PHP-SDK\/[0-9A-Za-z.-]*' "FlowPDF-PHP-SDK\/$VERSION"
# PHP: Packagist toma la versión del tag git (composer.json no declara "version").
