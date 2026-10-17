# Survival atlas-lab

Pack del servidor survival de atlas-lab (Minecraft 26.3, Fabric 0.19.5) y su página de descarga.

## Qué hay aquí
- `index.html`: la página de descarga (GitHub Pages).
- `pack.toml`, `index.toml`, `mods/`, `resourcepacks/`, `shaderpacks/`: el pack en formato packwiz. Prism lo lee al abrir el juego y se actualiza solo.
- `descargas/Survival-atlas-lab-Prism.zip`: instancia de Prism que apunta a `https://s1ns1kosiss.github.io/survival-pack/pack.toml`.
- `descargas/Survival-atlas-lab.mrpack`: el mismo pack para Modrinth App.

## Publicar
1. Crear el repositorio público `survival-pack` en GitHub y subir esta carpeta.
2. Settings → Pages → Branch `main`, carpeta `/ (root)`.
3. La página queda en `https://s1ns1kosiss.github.io/survival-pack/`.

## Actualizar el pack
Cambiar un mod también hay que hacerlo en el servidor, con la misma versión. Subir la versión en `pack.toml`, volver a generar `index.toml` y el `.mrpack`, y subir los cambios: Prism los descarga solo la próxima vez que abran el juego.
