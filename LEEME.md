# Survival atlas-lab

Pack del servidor survival de atlas-lab (Minecraft 26.3, Fabric 0.19.5) y su página de descarga.

## Qué hay aquí
- `index.html`: la página de descarga (GitHub Pages).
- `pack.toml`, `index.toml`, `mods/`, `resourcepacks/`, `shaderpacks/`: el pack en formato packwiz. Prism lo lee al abrir el juego y se actualiza solo.
- `descargas/Survival-atlas-lab-Prism.zip`: instancia de Prism que apunta a `https://s1ns1kosiss.github.io/Mods/pack.toml`.
- `descargas/Survival-atlas-lab.mrpack`: el mismo pack para Modrinth App.

## Publicar
1. Crear el repositorio público `Mods` en GitHub y subir esta carpeta.
2. Settings → Pages → Branch `main`, carpeta `/ (root)`.
3. La página queda en `https://s1ns1kosiss.github.io/Mods/`.

## Actualizar el pack
Cambiar un mod también hay que hacerlo en el servidor, con la misma versión. Subir la versión en `pack.toml`, volver a generar `index.toml` y el `.mrpack`, y subir los cambios: Prism los descarga solo la próxima vez que abran el juego.

## CurseForge y launcher oficial
- `descargas/Survival-atlas-lab-CurseForge.zip` (7 MB, publicado): `manifest.json` con 38 archivos que CurseForge descarga desde la página de cada autor, más 12 de licencia libre incluidos en `overrides` con su aviso (`LICENCIAS-pack.txt`). Fresh Flower Pots no va (no está en CurseForge y no se puede redistribuir). Se arma con `build_cf2.py` + `cf_match.py`.
- `Survival-atlas-lab-manual.zip` (71 MB, en el Escritorio, **fuera del repositorio**): para el launcher oficial; trae los mods adentro, así que se pasa solo por el grupo.
