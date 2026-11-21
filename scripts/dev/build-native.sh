#!/usr/bin/env bash
# Compila el motor nativo de FlowPDF con Docker (sin instalar Rust) y lo copia a la carpeta
# runtimes/ de cada SDK, para poder ejecutar los SDKs y los ejemplos en local.
#
#   scripts/dev/build-native.sh
#
# Genera:
#   linux-x64  libflowpdf_native.so   (compilación nativa en Linux)
#   win-x64    flowpdf_native.dll     (compilación cruzada MinGW; en CI se usa MSVC)
#
# Los binarios no se versionan (.gitignore): en los releases los compila .github/workflows/release.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export MSYS_NO_PATHCONV=1   # Git Bash: no traducir rutas tipo /src
host_path() { if command -v cygpath >/dev/null; then cygpath -m "$1"; else echo "$1"; fi; }

docker run --rm -v "$(host_path "$ROOT"):/src" -w /src \
  -v rf-cargo:/usr/local/cargo/registry -v flowpdf-dev-target:/src/target \
  rust:1-bookworm bash -euo pipefail -c '
    cargo build --release --lib
    apt-get update -qq && apt-get install -y -qq gcc-mingw-w64-x86-64 >/dev/null
    rustup target add x86_64-pc-windows-gnu >/dev/null
    cargo build --release --lib --target x86_64-pc-windows-gnu
    rm -rf natives && mkdir -p natives/linux-x64/native natives/win-x64/native
    cp target/release/libflowpdf.so natives/linux-x64/native/libflowpdf_native.so
    cp target/x86_64-pc-windows-gnu/release/flowpdf.dll natives/win-x64/native/flowpdf_native.dll'

bash "$ROOT/scripts/ci/stage.sh" --natives-only "$ROOT/natives"
echo "Listo: binarios nativos copiados a las carpetas runtimes/ de cada SDK."
