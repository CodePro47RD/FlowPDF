#!/usr/bin/env bash
# Recompila el motor a WebAssembly con Docker y actualiza los archivos del sitio:
#   docs/flowpdf.wasm           binario (se carga con fetch() en HTTP/HTTPS)
#   docs/flowpdf-wasm-data.js   el mismo binario en base64 (para abrir el sitio con file:// sin CORS)
#
#   scripts/dev/build-wasm.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export MSYS_NO_PATHCONV=1
host_path() { if command -v cygpath >/dev/null; then cygpath -m "$1"; else echo "$1"; fi; }

docker run --rm -v "$(host_path "$ROOT"):/src" -w /src \
  -v rf-cargo:/usr/local/cargo/registry -v flowpdf-dev-target:/src/target \
  rust:1-bookworm bash -euo pipefail -c '
    rustup target add wasm32-unknown-unknown >/dev/null
    cargo build --release --lib --target wasm32-unknown-unknown
    cp target/wasm32-unknown-unknown/release/flowpdf.wasm docs/flowpdf.wasm
    { printf "window.FLOWPDF_WASM_BASE64 = \""; base64 -w0 docs/flowpdf.wasm; printf "\";\n"; } > docs/flowpdf-wasm-data.js
    ls -la docs/flowpdf.wasm docs/flowpdf-wasm-data.js'
