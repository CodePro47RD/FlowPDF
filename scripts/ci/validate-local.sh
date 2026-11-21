#!/usr/bin/env bash
# Reproduce en local (con Docker) los jobs de .github/workflows/release.yml, SIN publicar nada.
#
#   scripts/ci/validate-local.sh [version] [pasos...]
#
#   version  versión de prueba a estampar (por defecto 0.0.0-rc.1)
#   pasos    subconjunto de: lint native crate nuget npm pypi maven php smoke   (por defecto: todos)
#
# Trabaja sobre una copia del repo en .ci-local/ (ignorada por git); el árbol real no se toca.
# Nota: win-x64 se compila aquí con MinGW (cross); en CI se compila con MSVC en Windows.
# "smoke" instala el .nupkg en una app de consola y genera un PDF en Linux (Docker) y en Windows (dotnet local).
set -euo pipefail

VERSION="${1:-0.0.0-rc.1}"; shift || true
STEPS="${*:-lint native crate nuget npm pypi maven php smoke}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORK="$ROOT/.ci-local"
SRC="$WORK/src"
export MSYS_NO_PATHCONV=1   # Git Bash: no traducir rutas tipo /src

# Ruta del host en formato que Docker Desktop entiende (C:/... en Windows)
host_path() { if command -v cygpath >/dev/null; then cygpath -m "$1"; else echo "$1"; fi; }

run() { # imagen  comando...   (monta la copia en /src)
  local image="$1"; shift
  docker run --rm -v "$(host_path "$SRC"):/src" -w /src \
    -v rf-cargo:/usr/local/cargo/registry -v rf-target:/src/target \
    -v rf-m2:/root/.m2 -v rf-nuget:/root/.nuget/packages \
    "$image" bash -euo pipefail -c "$*"
}

declare -A RESULT
step() { # nombre  función
  echo; echo "================ $1 ================"
  if "$2"; then RESULT[$1]="OK"; else RESULT[$1]="FALLÓ"; fi
}
want() { [[ " $STEPS " == *" $1 "* ]]; }

# --- copia limpia del repo (incluye archivos nuevos sin commit) ---------------
rm -rf "$SRC"; mkdir -p "$SRC"
(cd "$ROOT" && git ls-files -co --exclude-standard -z | grep -zv '^\.ci-local/' | xargs -0 tar -cf - ) | tar -xf - -C "$SRC"
echo "Copia del repo en $SRC (versión de prueba: $VERSION)"

# --- pasos (cada uno replica su job del workflow) -----------------------------
lint() {
  docker run --rm -v "$(host_path "$SRC"):/repo" -w /repo rhysd/actionlint:1.7.7 -color .github/workflows/release.yml .github/workflows/ci.yml
}

native() {
  # linux-x64 nativo + win-x64 por compilación cruzada MinGW (en CI se usa MSVC en Windows).
  run rust:1-bookworm "sed -i -E '0,/^version = \"[^\"]*\"/s//version = \"$VERSION\"/' Cargo.toml"
  run rust:1-bookworm '
    cargo test --release
    cargo build --release --lib
    apt-get update -qq && apt-get install -y -qq gcc-mingw-w64-x86-64 >/dev/null
    rustup target add x86_64-pc-windows-gnu >/dev/null
    cargo build --release --lib --target x86_64-pc-windows-gnu
    mkdir -p natives/linux-x64/native natives/win-x64/native
    cp target/release/libreportforge.so natives/linux-x64/native/libreportforge_native.so
    cp target/x86_64-pc-windows-gnu/release/reportforge.dll natives/win-x64/native/reportforge_native.dll
    ls -la natives/*/native'
}

stage() { run debian:bookworm-slim "bash scripts/ci/stage.sh '$VERSION'"; }

crate() {
  run rust:1-bookworm "
    sed -i -E '0,/^version = \"[^\"]*\"/s//version = \"$VERSION\"/' Cargo.toml
    cargo package --allow-dirty
    cargo package --allow-dirty --list
    ls -la target/package/*.crate"
}

nuget() {
  run mcr.microsoft.com/dotnet/sdk:10.0 '
    apt-get update -qq && apt-get install -y -qq unzip >/dev/null
    rm -rf out/nuget sdk/csharp/ReportForge/bin sdk/csharp/ReportForge/obj
    dotnet pack sdk/csharp/ReportForge/ReportForge.csproj -c Release -o out/nuget -p:GeneratePackageOnBuild=false
    unzip -l out/nuget/*.nupkg | grep "runtimes/linux-x64/native/libreportforge_native.so"'
}

npm_() {
  run node:20-bookworm '
    cd sdk/typescript
    npm ci && npm run build
    mkdir -p ../../out/npm && rm -f ../../out/npm/*.tgz && npm pack --pack-destination ../../out/npm
    tar -tzf ../../out/npm/*.tgz | grep "package/runtimes/linux-x64/native/libreportforge_native.so"'
}

pypi() {
  run python:3.12-slim '
    pip install -q --root-user-action=ignore --upgrade build twine
    rm -rf out/pypi && python -m build sdk/python --outdir out/pypi
    twine check out/pypi/*
    python -m zipfile -l out/pypi/*.whl | grep "reportforge/runtimes/linux-x64/native/libreportforge_native.so"'
}

maven() {
  run maven:3.9-eclipse-temurin-17 "
    mvn -B -q -f sdk/java/pom.xml -Prelease -Dgpg.skip verify
    ls -la sdk/java/target/*.jar
    jar tf sdk/java/target/reportforge-$VERSION.jar | grep 'runtimes/linux-x64/native/libreportforge_native.so'"
}

php() {
  # composer:2 (Alpine) no trae bash: se usa sh como entrypoint
  docker run --rm -v "$(host_path "$SRC"):/src" -w /src --entrypoint sh composer:2 -euc "
    apk add -q jq zip >/dev/null
    rm -rf out/php && mkdir -p out/php
    cp -R sdk/php/src sdk/php/runtimes sdk/php/README.md out/php/
    cp LICENSE out/php/
    jq 'del(.version)' sdk/php/composer.json > out/php/composer.json
    (cd out/php && zip -qr ../reportforge-php-$VERSION.zip .)
    cd out/php && composer validate --strict --no-check-publish
    find . -path '*native*' -type f"
}

# Prueba de humo: instala el .nupkg en una app de consola, genera un PDF y extrae su texto.
smoke_linux() {
  run mcr.microsoft.com/dotnet/sdk:10.0 "
    rm -rf /tmp/smoke && cp -R scripts/ci/smoke/dotnet /tmp/smoke
    NUGET_PACKAGES=/tmp/nuget-fresh dotnet run --project /tmp/smoke -c Release \
      -p:ReportForgeVersion=$VERSION -p:ReportForgeFeed=/src/out/nuget"
}
smoke_windows() {
  # En el host: requiere Windows + dotnet SDK 10. Caché de paquetes aislada para no reutilizar
  # un ReportForge viejo con la misma versión.
  [[ "${OS:-}" == Windows_NT ]] || { echo "No es Windows; se omite"; return 0; }
  command -v dotnet >/dev/null || { echo "dotnet no está instalado; se omite"; return 0; }
  rm -rf "$WORK/nuget-fresh" "$WORK/smoke-win" && cp -R "$SRC/scripts/ci/smoke/dotnet" "$WORK/smoke-win"
  NUGET_PACKAGES="$(host_path "$WORK/nuget-fresh")" dotnet run --project "$(host_path "$WORK/smoke-win")" -c Release \
    -p:ReportForgeVersion="$VERSION" -p:ReportForgeFeed="$(host_path "$SRC/out/nuget")"
}

want lint   && step lint   lint
want native && step native native
if want nuget || want npm || want pypi || want maven || want php; then
  [[ -d "$SRC/natives" ]] || step native native
  step stage stage
fi
want crate  && step crate  crate
want nuget  && step nuget  nuget
want npm    && step npm    npm_
want pypi   && step pypi   pypi
want maven  && step maven  maven
want php    && step php    php
if want smoke; then
  [[ -n "$(ls "$SRC"/out/nuget/*.nupkg 2>/dev/null)" ]] || step nuget nuget
  step smoke-linux   smoke_linux
  step smoke-windows smoke_windows
fi

echo; echo "================ RESUMEN ================"
fail=0
for k in lint native stage crate nuget npm pypi maven php smoke-linux smoke-windows; do
  [[ -n "${RESULT[$k]:-}" ]] || continue
  printf '  %-8s %s\n' "$k" "${RESULT[$k]}"
  [[ "${RESULT[$k]}" == OK ]] || fail=1
done
echo "Paquetes generados en: $SRC/out"
exit $fail
