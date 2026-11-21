# Publicación automática de paquetes (GitHub Actions)

El workflow [`.github/workflows/release.yml`](../.github/workflows/release.yml) compila el motor Rust,
empaqueta los SDKs con esos binarios y los publica en los registros públicos.

| SDK | Registro | Nombre del paquete | Instalación |
|---|---|---|---|
| C# | NuGet | `ReportForge` | `dotnet add package ReportForge` |
| TypeScript/JS | npm | `reportforge` | `npm install reportforge` |
| Python | PyPI | `reportforge-sdk` (import: `reportforge`) | `pip install reportforge-sdk` |
| Java | Maven Central | `io.github.codepro47rd:reportforge` | ver abajo |
| PHP | Packagist (vía repo espejo) | `reportforge/reportforge` | `composer require reportforge/reportforge` |
| Rust | crates.io | `reportforge` | `cargo add reportforge` |

> `reportforge` ya está tomado en PyPI por otro proyecto, por eso la distribución Python se llama `reportforge-sdk`.

## Cómo funciona

1. **`native`**: `cargo test` + `cargo build --release` en `win-x64` (MSVC, CRT estático) y `linux-x64` (Ubuntu 22.04, glibc 2.35).
2. **`pack-*`**: [`scripts/ci/stage.sh`](../scripts/ci/stage.sh) copia esos binarios a `runtimes/` de cada SDK
   (reemplazando los versionados en git) y estampa la versión del tag en todos los manifiestos. Cada job
   verifica que el binario quedó dentro del paquete.
3. **`publish-*`**: solo corre si **todos** los `pack-*` terminaron bien.
4. **`github-release`**: en push de tag, adjunta paquetes y binarios al GitHub Release.

## Cómo lanzar un release

```bash
git tag v2.1.1
git push origin v2.1.1          # compila y publica 2.1.1 en todos los registros
```

Prueba sin publicar: **Actions → Release Packages → Run workflow**, versión `2.1.1`, `publish` desmarcado.
Los paquetes quedan como artefactos descargables del run.

Pre-releases: solo `-alpha`, `-beta` o `-rc` con número opcional (`v2.2.0-beta.1`), porque es el único formato
válido a la vez en SemVer y en PEP 440 (PyPI lo publica como `2.2.0b1`). Se publican en npm con el dist-tag `next`
y se marcan como pre-release en GitHub. Algo como `-preview` o `-test` se rechaza al inicio del workflow.

### Validar en local antes de etiquetar (Docker)

```bash
bash scripts/ci/validate-local.sh                 # todo, con versión 0.0.0-rc.1
bash scripts/ci/validate-local.sh 2.1.1 pypi php  # solo algunos pasos
```

Corre en contenedores los mismos pasos de los jobs `pack-*` (más `actionlint` sobre los workflows) sobre una copia
del repo en `.ci-local/`; no publica nada. Los paquetes quedan en `.ci-local/src/out/`. El binario `win-x64` no se
compila en local (requiere Windows/MSVC): se usa el que está en git.

> Una versión publicada **no se puede volver a subir** en ningún registro. Si un registro falla y los demás no,
> corrige y publica la siguiente versión de parche.

## Configuración inicial (una sola vez)

Secrets y variables van en **Settings → Secrets and variables → Actions** del repo (o de la organización).
Se requiere rol admin. No se usan *environments*: en repos privados solo existen con GitHub Pro/Team/Enterprise.

### Secrets

| Secret | De dónde sale |
|---|---|
| `NPM_TOKEN` | npmjs.com → Access Tokens → *Granular* con permiso *Read and write* y *Bypass 2FA* |
| `CARGO_REGISTRY_TOKEN` | crates.io → Account Settings → API Tokens (scope `publish-new`, `publish-update`) |
| `MAVEN_CENTRAL_USERNAME` / `MAVEN_CENTRAL_PASSWORD` | central.sonatype.com → *View Account* → *Generate User Token* |
| `MAVEN_GPG_PRIVATE_KEY` | `gpg --armor --export-secret-keys <KEY_ID>` (bloque completo) |
| `MAVEN_GPG_PASSPHRASE` | passphrase de esa clave |
| `PHP_MIRROR_DEPLOY_KEY` | Clave **privada** SSH (ed25519) cuya pública está como *deploy key* con escritura en el repo espejo (ver abajo) |
| `PACKAGIST_TOKEN` *(opcional)* | packagist.org → Profile → API Token (solo si no usas la integración de GitHub) |

### Variables (Settings → Secrets and variables → Actions → *Variables*)

| Variable | Valor |
|---|---|
| `NUGET_USER` | usuario (nombre de perfil, no email) de nuget.org dueño de la política de Trusted Publishing |
| `PHP_MIRROR_REPO` | ej. `CodePro47RD/reportforge-php` |
| `PACKAGIST_USERNAME` *(opcional)* | usuario de Packagist |

### Por registro

- **NuGet (Trusted Publishing, sin API key)**: nuget.org → tu usuario → *Trusted Publishing* → *Create*:
  Package Owner = la organización de NuGet, Repository Owner = `CodePro47RD`, Repository `ReportForge`,
  Workflow File `release.yml`, **Environment vacío**, scope *Push new packages and package versions*,
  glob `ReportForge`. En repos privados la política queda temporal (7 días) hasta el primer publish exitoso.
- **PyPI (Trusted Publishing, sin token)**: pypi.org → *Your projects* → *Publishing* → *Add a new pending publisher*:
  proyecto `reportforge-sdk`, owner `CodePro47RD`, repo `ReportForge`, workflow `release.yml`, **environment vacío**.
- **Maven Central**: en central.sonatype.com → *Namespaces* → *Add Namespace* `io.github.codepro47rd`. Sonatype
  da una clave de verificación: crear en la org un repo **público** temporal con ese nombre exacto, pulsar
  *Verify* y luego borrarlo. Publicar la clave GPG pública en un keyserver:
  `gpg --keyserver keyserver.ubuntu.com --send-keys <KEY_ID>`.
- **PHP / Packagist**: repo **público** `PHP_MIRROR_REPO` con un commit inicial. El push usa una *deploy key* (requiere
  *Deploy keys* habilitadas en la org): `ssh-keygen -t ed25519 -N "" -f k`, luego
  `gh repo deploy-key add k.pub --repo <espejo> --allow-write` y `gh secret set PHP_MIRROR_DEPLOY_KEY < k`; borrar `k`.
  Tras el primer release, registrarlo en packagist.org → *Submit* y conectar la integración de GitHub para que
  cada tag nuevo se actualice solo.
- **npm / crates.io**: el primer publish crea el paquete; no hace falta registrarlo antes.

## Agregar macOS

En `release.yml`, descomenta las entradas `osx-x64` / `osx-arm64` de la matriz `native`. Los SDKs ya buscan
`libreportforge_native.dylib`; el de C# hoy solo resuelve `osx-x64`, así que para Apple Silicon hay que
agregar `osx-arm64` en `sdk/csharp/ReportForge/Native/ReportForgeEngine.cs`. Los runners macOS consumen
10× minutos en repos privados.
