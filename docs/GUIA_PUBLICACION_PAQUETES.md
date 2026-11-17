# Guía Oficial de Registro y Publicación de Paquetes — ReportForge v2.0

> Documento técnico de referencia para registrar cuentas, configurar credenciales de seguridad (2FA, API Keys, Tokens, GPG) y publicar las librerías oficiales de **ReportForge v2.0** en los repositorios públicos de **C# (.NET)**, **TypeScript / JavaScript**, **Python**, **PHP**, **Java** y **Rust**.

---

## 📑 Índice de Contenidos
1. [Matriz Comparativa de Registros Oficiales](#1-matriz-comparativa-de-registros-oficiales)
2. [C# (.NET) — NuGet Gallery (`nuget.org`)](#2-c-net--nuget-gallery-nugetorg)
3. [TypeScript / JavaScript — npm Registry (`npmjs.com`)](#3-typescript--javascript--npm-registry-npmjscom)
4. [Python — PyPI (`pypi.org`)](#4-python--pypi-pypiorg)
5. [PHP — Packagist (`packagist.org`)](#5-php--packagist-packagistorg)
6. [Java — Maven Central (`central.sonatype.com`)](#6-java--maven-central-centralsonatypecom)
7. [Rust — Crates.io (`crates.io`)](#7-rust--cratesio-cratesio)
8. [Automatización con GitHub Actions (CI/CD)](#8-automatización-con-github-actions-cicd)
9. [Buenas Prácticas de Versionado Semántico y Seguridad](#9-buenas-prácticas-de-versionado-semántico-y-seguridad)

---

## 1. Matriz Comparativa de Registros Oficiales

| Ecosistema | Registro Oficial | Formato de Paquete | Autenticación Requerida | Comando de Publicación |
| :--- | :--- | :--- | :--- | :--- |
| **C# (.NET)** | [nuget.org](https://www.nuget.org/) | `.nupkg` | Cuenta Microsoft + API Key | `dotnet nuget push <archivo>.nupkg` |
| **TypeScript** | [npmjs.com](https://www.npmjs.com/) | `.tgz` o carpeta | Cuenta npm + 2FA Obligatorio | `npm publish <archivo>.tgz --access public` |
| **Python** | [pypi.org](https://pypi.org/) | `.whl` / `.tar.gz` | Cuenta PyPI + 2FA + API Token | `twine upload <archivo>.whl` |
| **PHP** | [packagist.org](https://packagist.org/) | Repo Git público | Cuenta GitHub vinculada | Envío de URL vía web / GitHub Webhook |
| **Java** | [central.sonatype.com](https://central.sonatype.com/) | Bundle `.jar` + `.pom` | Cuenta Sonatype + Clave GPG + Token | Portal Web o `mvn deploy` |
| **Rust** | [crates.io](https://crates.io/) | Código fuente Crate | Cuenta GitHub + Cargo Token | `cargo publish` |

---

## 2. C# (.NET) — NuGet Gallery (`nuget.org`)

El paquete oficial compilado se ubica en: `docs/packages/ReportForge.2.0.0.nupkg`.

### 2.1 Registro de Cuenta
1. Ingresa a [nuget.org](https://www.nuget.org/) y haz clic en **Sign in**.
2. Autentícate con una cuenta de Microsoft (personal o corporativa).
3. Configura tu nombre de usuario público o crea una Organización si prefieres publicar bajo la marca `ReportForge`.

### 2.2 Generación de API Key
1. Haz clic en tu nombre de usuario en la esquina superior derecha y selecciona **API Keys**.
2. Pulsa en **+ Create**.
3. Completa los campos:
   - **Key Name**: `reportforge-release-key`
   - **Expires in**: Selecciona 365 días (o 90 días por seguridad).
   - **Package Scopes**: Marca **Push** y **Push new packages and package versions**.
   - **Glob Pattern**: Introduce `ReportForge*` o `*`.
4. Haz clic en **Create** y presiona **Copy** (la clave solo se muestra una vez; guárdala en tu gestor de secretos).

### 2.3 Comando de Publicación CLI
Abre tu terminal en la raíz del proyecto y ejecuta:

```powershell
dotnet nuget push "docs/packages/ReportForge.2.0.0.nupkg" --api-key <TU_API_KEY_DE_NUGET> --source https://api.nuget.org/v3/index.json --skip-duplicate
```

### 2.4 Verificación
- En aproximadamente 5 a 10 minutos, NuGet realiza la indexación y el análisis antivirus.
- Tu paquete quedará público en `https://www.nuget.org/packages/ReportForge/`.
- Cualquier usuario podrá instalarlo mediante:
  ```powershell
  dotnet add package ReportForge
  ```

---

## 3. TypeScript / JavaScript — npm Registry (`npmjs.com`)

El paquete empaquetado se ubica en: `docs/packages/reportforge-2.0.0.tgz`.

### 3.1 Registro de Cuenta
1. Regístrate en [npmjs.com/signup](https://www.npmjs.com/signup).
2. Verifica tu correo electrónico haciendo clic en el enlace de confirmación.

### 3.2 Activación de 2FA (Requisito Obligatorio)
npm exige de forma obligatoria el uso de autenticación de dos factores (2FA) para publicar:
1. Ve a **Account Settings** ➔ **Two-Factor Authentication (2FA)**.
2. Escanea el código QR con tu aplicación autenticadora (Google Authenticator, 1Password o Authy) e introduce el código numérico.

### 3.3 Inicio de Sesión en la Terminal
Desde tu consola ejecuta:
```powershell
npm login
```
Introduce:
- Username
- Password
- Email (te enviará un código temporal de un solo uso por correo)
- Código 2FA de tu aplicación móvil.

### 3.4 Publicación del Paquete
```powershell
npm publish "docs/packages/reportforge-2.0.0.tgz" --access public
```

*Si deseas publicar directamente desde la carpeta del SDK:*
```powershell
cd sdk/typescript
npm publish --access public
```

### 3.5 Verificación
- Tu paquete estará activo de inmediato en `https://www.npmjs.com/package/reportforge`.
- Instalación pública:
  ```powershell
  npm install reportforge
  ```

---

## 4. Python — PyPI (`pypi.org`)

El paquete wheel compatible se ubica en: `docs/packages/reportforge-2.0.0-py3-none-any.whl`.

### 4.1 Registro de Cuenta
1. Crea una cuenta en [pypi.org/account/register](https://pypi.org/account/register/).
2. Confirma tu dirección de correo electrónico.

### 4.2 Configuración de 2FA y API Token
PyPI no permite autenticarse con usuario y contraseña tradicionales por terminal; requiere un Token de API:
1. Ve a **Account settings** ➔ **Two-factor authentication (2FA)** y configúralo.
2. Baja a la sección **API tokens** y haz clic en **Add API token**.
3. Configura:
   - **Token name**: `reportforge-publisher`
   - **Scope**: `Entire account (all projects)` (para el primer release).
4. Copia el token generado que comienza con `pypi-...`.

### 4.3 Publicación con Twine
Asegúrate de tener instalada la herramienta oficial `twine`:
```powershell
pip install --upgrade twine
```

Ejecuta la subida indicando `__token__` como usuario:
```powershell
twine upload "docs/packages/reportforge-2.0.0-py3-none-any.whl" -u __token__ -p <TU_PYPI_API_TOKEN>
```

### 4.4 Verificación
- Disponible al instante en `https://pypi.org/project/reportforge/`.
- Instalación pública:
  ```powershell
  pip install reportforge
  ```

---

## 5. PHP — Packagist (`packagist.org`)

Packagist es el repositorio central de Composer. No aloja archivos binarios comprimidos directamente, sino que rastrea y sincroniza repositorios públicos de Git (GitHub, GitLab, Bitbucket).

### 5.1 Preparación del Repositorio en GitHub
1. Sube el código de `sdk/php/` a un nuevo repositorio público en GitHub:
   - Ejemplo: `https://github.com/tu-usuario/reportforge-php`
2. Asegúrate de que en la raíz del repositorio esté el archivo `composer.json` con el nombre `"reportforge/reportforge"`.
3. Crea un tag de versión y súbelo a GitHub:
   ```bash
   git tag v2.0.0
   git push origin v2.0.0
   ```

### 5.2 Registro en Packagist
1. Entra a [packagist.org](https://packagist.org/) y selecciona **Sign up**.
2. **Recomendado**: Haz clic en **Use GitHub** para iniciar sesión con un solo clic y vincular tus permisos automáticamente.

### 5.3 Envío del Paquete (Submit)
1. En el menú superior de Packagist, haz clic en **Submit**.
2. Pega la URL completa de tu repositorio:
   `https://github.com/tu-usuario/reportforge-php`
3. Haz clic en **Check**. Packagist leerá tu `composer.json`.
4. Si no hay conflictos de nombres, presiona **Submit**.

### 5.4 Sincronización Automática (GitHub Webhook)
Para que cada nuevo tag (`v2.0.1`, `v2.1.0`) se publique automáticamente en Packagist:
1. En la página de tu paquete en Packagist, copia tu **API Token** desde tu perfil.
2. En GitHub, ve a **Settings** de tu repositorio ➔ **Webhooks** ➔ **Add webhook**.
3. En Payload URL pega la URL del webhook de Packagist y guarda.

---

## 6. Java — Maven Central (`central.sonatype.com`)

Maven Central es el repositorio estándar consultado por Maven, Gradle y Kotlin. Desde 2024, Sonatype habilitó el **Central Publisher Portal** que reemplaza el antiguo flujo de tickets JIRA.

### 6.1 Registro en Sonatype Central
1. Entra a [central.sonatype.com](https://central.sonatype.com/) e inicia sesión con tu cuenta de GitHub.

### 6.2 Verificación de Namespace (GroupId)
Maven Central requiere demostrar que eres dueño del prefijo de tu paquete:
- **Opción A (Dominio Propio - ej. `dev.reportforge`)**: En el portal de Sonatype, añade el namespace. Te darán un valor alfanumérico que debes agregar como registro DNS tipo **TXT** en tu dominio.
- **Opción B (GitHub Namespace - ej. `io.github.<tu-usuario>`)**: Creas un repositorio público vacío en tu cuenta de GitHub con el nombre temporal que Sonatype te indique y presionas "Verify".

### 6.3 Generación de Clave Criptográfica GPG (Obligatoria)
Todo archivo subido a Maven Central debe estar firmado digitalmente:
```bash
# 1. Generar la clave
gpg --gen-key

# 2. Listar la clave generada
gpg --list-keys --keyid-format LONG

# 3. Publicar la clave pública a los keyservers de Ubuntu / OpenPGP
gpg --keyserver keyserver.ubuntu.com --send-keys <KEY_ID>
```

### 6.4 Publicación del Paquete
- **Vía Web Portal**:
  1. En [central.sonatype.com](https://central.sonatype.com/), ve a **Publish** ➔ **Upload Component**.
  2. Empaqueta tu `.jar`, el archivo `-javadoc.jar`, el archivo `-sources.jar` y el archivo `pom.xml` con sus respectivas firmas `.asc` en un archivo ZIP.
  3. Sube el ZIP y pulsa **Publish**.
- **Vía Maven Plugin**:
  Configura el plugin `central-publishing-maven-plugin` en tu `pom.xml` y ejecuta `mvn clean deploy`.

---

## 7. Rust — Crates.io (`crates.io`)

Si deseas distribuir el motor nativo de ReportForge directamente a la comunidad de Rust para ser consumido en proyectos `Cargo.toml`.

### 7.1 Registro
1. Ingresa a [crates.io](https://crates.io/) e inicia sesión con tu cuenta de GitHub.

### 7.2 Obtención de API Token
1. En tu perfil, haz clic en **Account Settings** ➔ **API Tokens**.
2. Pulsa en **New Token**, dale un nombre (ej. `cargo-publish-token`) y copia el secreto.

### 7.3 Autenticación de Cargo
En tu terminal:
```powershell
cargo login <TU_TOKEN_DE_CRATES_IO>
```
*Esto guarda la credencial en `~/.cargo/credentials.toml`.*

### 7.4 Publicación
Verifica que tu `Cargo.toml` tenga los campos `license`, `description`, `repository` y `readme`:
```powershell
cargo publish
```

---

## 8. Automatización con GitHub Actions (CI/CD)

Puedes automatizar la publicación simultánea en todos los registros cada vez que publiques un Release en GitHub mediante el siguiente flujo de trabajo:

```yaml
# .github/workflows/publish-packages.yml
name: Publicación Oficial de Paquetes

on:
  release:
    types: [published]

jobs:
  publish-nuget:
    name: Publicar en NuGet (C#)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'
      - name: Push NuGet
        run: dotnet nuget push docs/packages/*.nupkg --api-key ${{ secrets.NUGET_API_KEY }} --source https://api.nuget.org/v3/index.json --skip-duplicate

  publish-npm:
    name: Publicar en npm (TypeScript)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20.x'
          registry-url: 'https://registry.npmjs.org'
      - name: Publish npm
        run: npm publish docs/packages/reportforge-*.tgz --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

  publish-pypi:
    name: Publicar en PyPI (Python)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install Twine
        run: pip install twine
      - name: Upload to PyPI
        run: twine upload docs/packages/*.whl -u __token__ -p ${{ secrets.PYPI_API_TOKEN }}
```

---

## 9. Buenas Prácticas de Versionado Semántico y Seguridad

1. **Versionado Semántico (SemVer - `MAJOR.MINOR.PATCH`)**:
   - `MAJOR` (ej. `3.0.0`): Cambios incompatibles o modificaciones en el C-ABI.
   - `MINOR` (ej. `2.1.0`): Nuevos componentes o builders sin romper la API existente.
   - `PATCH` (ej. `2.0.1`): Correcciones de errores y optimizaciones internas.
2. **Inmutabilidad de Paquetes**: Tanto NuGet, npm como PyPI **no permiten sobrescribir una versión ya publicada**. Si cometes un error en la versión `2.0.0`, debes corregir y publicar como `2.0.1`.
3. **Gestión Segura de Secretos**: Nunca guardes tus API Keys o Tokens en repositorios públicos. Utiliza siempre los secretos encriptados de GitHub (`Repository Secrets`) o variables de entorno del sistema.
