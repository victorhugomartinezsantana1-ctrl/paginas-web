# Auditoría inicial del sitio devlog

Fecha: 2026-10-27 · URL pública: https://kind-mud-077d38b10.1.azurestaticapps.net/

## 1. Arquitectura y despliegue (verificado)

| Aspecto | Hallazgo |
|---|---|
| Repositorio | `C:\Users\victo\OneDrive\Desktop\paginas web` (raíz del repo propio del sitio), remoto `origin` = `victorhugomartinezsantana1-ctrl/paginas-web` (público) |
| Rama de producción | `main` (el push a `main` despliega; los pull requests crean entornos de previsualización) |
| Tipo de sitio | HTML estático escrito a mano + Tailwind por CDN (sin framework, sin paso de compilación) |
| Despliegue | GitHub Actions (`.github/workflows/azure-static-web-apps-kind-mud-077d38b10.yml`) con `Azure/static-web-apps-deploy@v1`; `app_location: "/"`, `api_location: ""`, `output_location: "."` |
| Consecuencia | Todo lo que esté en la raíz del repositorio se publica tal cual. Los HTML publicados viven en `articulos/<slug>.html`. |
| Configuración de Azure | `staticwebapp.config.json`: caché de `/assets/*` con revalidación, cabeceras de seguridad, rutas de login bloqueadas salvo GitHub y Microsoft |
| Autenticación | Integrada de Azure Static Web Apps (`/.auth/*`), página `login.html` |
| Navegación | Cuadrícula de tarjetas en `index.html`; cada página enlaza a inicio/artículos/contacto |
| Sitemap / robots | `sitemap.xml` y `robots.txt` escritos a mano (ahora generados también por `editorial/herramientas/construir.py`) |
| Pruebas existentes | Ninguna en el repositorio |
| Herramientas locales | Python 3.14, Node 24, git |

La URL pública no demuestra por sí sola que se pueda desplegar: aquí sí se ha comprobado (el push a `main` ejecuta el workflow y el cambio aparece en la URL pública, como en los despliegues anteriores de esta sesión).

## 2. Contenido existente (16 artículos)

Recuento con `editorial/herramientas/contar_palabras.py` (sin código, sin plantilla):

| Artículo | Etiqueta | Fecha | Palabras |
|---|---|---|---:|
| kubernetes-arquitectura-interna | devops | 2026-10-27 | 1.240 |
| rust-vs-cpp-sistemas-embebidos | hardware | 2026-10-27 | 1.003 |
| terraform-infraestructura-codigo | azure | 2026-10-27 | 774 |
| git-rebase-interactivo | git | 2026-09-17 | 516 |
| linux-grep-sed-awk | linux | 2026-10-01 | 349 |
| azure-static-web-apps | azure | 2026-10-20 | 346 |
| github-actions-cache | devops | 2026-10-14 | 327 |
| neovim-ide-terminal | neovim | 2026-10-26 | 318 |
| particiones-dualboot | sysadmin | 2026-10-24 | 311 |
| docker-multi-stage | docker | 2026-09-24 | 301 |
| esp32-control-motores | iot | 2026-10-22 | 284 |
| python-metodos-numericos | python | 2026-10-20 | 269 |
| arch-hyprland-wayland | linux | 2026-10-25 | 229 |
| obsidian-llm-python | ai | 2026-10-21 | 227 |
| python-pathlib | python | 2026-10-08 | 194 |
| cpp-ncurses-terminal | cpp | 2026-10-23 | 156 |
| **Total** | | | **6.844** |

Media ≈ 430 palabras por artículo; mediana ≈ 315.

## 3. Temática, audiencia y estilo

- **Idioma y audiencia:** español, lectores técnicos (estudiantes de ingeniería y desarrolladores/sysadmins) interesados en programación de sistemas, DevOps/cloud, Linux, electrónica embebida (ESP32) y herramientas de terminal.
- **Categorías presentes:** DevOps/cloud (azure, docker, kubernetes, terraform, GitHub Actions), Linux y herramientas (grep/sed/awk, Hyprland, dual-boot, Neovim), embebidos/IoT (ESP32, Rust vs C++, ncurses), Python (pathlib, métodos numéricos, Obsidian+LLM), Git.
- **Estilo visual:** tema claro, tipografía Inter, código en JetBrains Mono, tarjetas con barra de color, huecos de AdSense comentados.
- **Profundidad habitual:** guías breves de 150–500 palabras (solo 3 superan las 700).

## 4. Problemas detectados

| # | Problema | Gravedad | Estado |
|---|---|---|---|
| 1 | Las etiquetas "N min de lectura" (12–35 min) eran falsas: no correspondían al texto real (1–6 min) | Alta (información engañosa) | **Corregido** con `construir.py --recalcular-lecturas` (200 palabras/min) |
| 2 | Canonical, `og:url`, JSON-LD, sitemap y robots apuntaban a `TU-DOMINIO.com`, un dominio inexistente | Alta (SEO) | **Corregido**: apuntan a la URL pública real (`SITE_URL` en `construir.py`) |
| 3 | `og:image` referenciaba una imagen inexistente | Media | **Corregido**: se eliminó la etiqueta hasta tener imagen real |
| 4 | Contenido escaso para monetizar con AdSense (6.844 palabras en 16 páginas) | Alta | En curso: plan de 30 investigaciones de ≥ 5.000 palabras |
| 5 | Algunos artículos mezclan secciones sin ejemplos ni fuentes citadas | Media | Pendiente: no se reescriben en este proyecto; se enlazarán desde los nuevos |
| 6 | Sin referencias bibliográficas en ningún artículo | Media | Los nuevos incluyen referencias verificadas |
| 7 | Tailwind por CDN (no recomendado en producción por Tailwind) | Baja/Media | Pendiente: requeriría un paso de compilación; se registra como decisión del propietario |
| 8 | Carpeta `init/` (repositorio git vacío anidado, ignorada en `.gitignore`) | Baja | Pendiente de borrado por el propietario (no se elimina por no ser mía) |
| 9 | Sin pruebas automáticas ni validación de enlaces | Media | **Añadido**: `editorial/herramientas/verificar.py` |
| 10 | AdSense: sin ID de editor ni dominio propio | Informativo | Fuera de alcance editorial; documentado en la conversación |

## 5. Huecos temáticos (insumo del plan)

Cubiertos superficialmente: Git, contenedores, Kubernetes, ESP32, Python.
Sin cobertura: redes (TCP, DNS, TLS, HTTP/3), bases de datos (PostgreSQL, índices, SQLite), observabilidad, seguridad de la cadena de suministro, systemd, asyncio y memoria en Python, C++ moderno, Rust (propiedad), buses de comunicación (I2C/SPI/UART), control PID, MQTT, rendimiento y accesibilidad web, WebAssembly, criptografía aplicada, scripting en Bash.

## 6. Decisiones de diseño del proyecto editorial

- El espacio de trabajo (`editorial/`) vive en el repositorio para quedar versionado, pero se **bloquea en la web** con una regla `404` en `staticwebapp.config.json` (`/editorial/*`).
- Fuente de verdad del texto: `editorial/articulos/ART-xxx/cuerpo.html` + `meta.json`. Los HTML independientes publicados se generan en `articulos/<slug>.html` (donde el sitio los sirve).
- Recuento de palabras: `contar_palabras.py` (excluye código, anuncios, índices, referencias y plantilla).
