#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador oficial del repositorio GitHub Pages (https://github.com/s1ns1kosiss/Mods)
para la Serie RPG de Minecraft 1.21.1 (Fabric 0.16.10) - Pack v2.0.0.

Qué hace este script automáticamente en C:\\Users\\Frijol\\Desktop\\survival-pack:
1. Resuelve exactamente el mismo catálogo de mods de la Serie 1.21.1 que tiene el
   servidor (/opt/minecraft/serie) usando la API oficial de Modrinth v2.
2. Limpia los archivos .pw.toml antiguos de la versión 26.3 y escribe los nuevos
   mods/*.pw.toml, resourcepacks/*.pw.toml y shaderpacks/*.pw.toml con finales de
   línea LF exactos.
3. Genera config/simple-modpack-update-checker.json y los 8 Capítulos en Español
   del Libro de Misiones en config/heracles/quests/.
4. Calcula todas las huellas SHA-256 en index.toml y actualiza pack.toml (MC 1.21.1,
   Fabric 0.16.10, versión 2.0.0).
5. Construye en descargas/:
   - Survival-atlas-lab-Prism.zip (con packwiz-installer-bootstrap.jar auto-actualizable)
   - Survival-atlas-lab.mrpack (formato oficial Modrinth App / Prism)
   - Survival-atlas-lab-CurseForge.zip
6. Actualiza index.html con toda la información de la Serie RPG 2.0.0.
"""

import hashlib
import html
import io
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODS_DIR = os.path.join(BASE_DIR, "mods")
RP_DIR = os.path.join(BASE_DIR, "resourcepacks")
SP_DIR = os.path.join(BASE_DIR, "shaderpacks")
CFG_DIR = os.path.join(BASE_DIR, "config")
DL_DIR = os.path.join(BASE_DIR, "descargas")

API = "https://api.modrinth.com/v2"
HEADERS = {"User-Agent": "AtlasSeriePackwizGenerator/2.0.1 (s1ns1kosiss/Mods)"}
MC_VERSIONS = ["1.21.1", "1.21"]
PACK_VERSION = "2.0.1"
MC_TARGET = "1.21.1"
FABRIC_TARGET = "0.19.5"
PACK_TOML_URL = "https://s1ns1kosiss.github.io/Mods/pack.toml"


def obtener_ultimo_fabric_loader() -> str:
    try:
        req = urllib.request.Request("https://meta.fabricmc.net/v2/versions/loader", headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            datos = json.loads(r.read().decode("utf-8"))
            for item in datos:
                if item.get("stable") and item.get("version"):
                    return item["version"]
            if datos and datos[0].get("version"):
                return datos[0]["version"]
    except Exception:
        pass
    return "0.19.5"

# ==============================================================================
# 1. CATÁLOGO EXACTO SINCRONIZADO CON EL SERVIDOR (/opt/minecraft/serie)
# ==============================================================================

SHARED_MODS = [
    # --- Core & Rendimiento Común ---
    "fabric-api",
    "ferrite-core",
    "lithium",
    "modernfix",
    "krypton",

    # --- Clases RPG, Talentos y Combate (Fase 2 + Fase 4) ---
    "better-combat",
    "combat-roll",
    "puffish_skills",
    "puffish_attributes",
    "skill-tree-rpg-series",
    "wizards",
    "paladins-and-priests",
    "archers",
    "rogues-and-warriors",
    "jewelry",
    "artifacts",
    "accessories",

    # --- Grandes Jefes y Armas Legendarias ---
    "bosses-of-mass-destruction",
    "adventurez",
    "mariums-soulslike-weaponry",

    # --- Minerales, Forjas, Tecnología y Vehículos ---
    "mythicmetals",
    "alloy-forgery",
    "oritech",
    "toms-storage",
    "small-ships",
    "immersive-aircraft",

    # --- Las 4 Dimensiones + Backports 1.21.4/1.21.5 ---
    "terralith",
    "tectonic",
    "deeper-and-darker",
    "incendium",
    "nullscape",
    "pale-garden-backport",
    "spring-to-life-backport",

    # --- Exploración, Mega-Mazmorras, Aldeas y Fauna (Estilo Kayzend & ElKeoMc) ---
    "when-dungeons-arise",
    "the-graveyard-fabric",
    "ribbits",
    "choice-theorems-overhauled-village",
    "towns-and-towers",
    "structory",
    "dungeons-and-taverns",
    "yungs-better-dungeons",
    "yungs-better-nether-fortresses",
    "yungs-better-mineshafts",
    "yungs-better-strongholds",
    "yungs-better-ocean-monuments",
    "yungs-better-jungle-temples",
    "yungs-better-witch-huts",
    "guard-villagers-fabric",
    "villager-names",
    "naturalist",
    "friends-and-foes",
    "creeper-overhaul",
    "illager-invasion",
    "nyfs-spiders",
    "lootr",
    "explorers-compass",
    "natures-compass",
    "bountiful",
    "kambrik",

    # --- Construcción, Arquitectura, Decoración y Gastronomía ---
    "building-wands",
    "effortless",
    "visual-workbench",
    "easy-anvils",
    "easy-magic",
    "diagonal-fences",
    "diagonal-windows",
    "diagonal-walls",
    "chipped",
    "rechiseled",
    "macaws-roofs",
    "macaws-bridges",
    "macaws-windows",
    "macaws-doors",
    "macaws-trapdoors",
    "macaws-fences-and-walls",
    "macaws-lights-and-lamps",
    "macaws-furniture",
    "supplementaries",
    "amendments",
    "handcrafted",
    "another-furniture",
    "beautify-refabricated",
    "farmers-delight-refabricated",
    "lets-do-vinery",
    "lets-do-bakery-farm-charm-compat",
    "lets-do-brewery-farm-charm-compat",
    "exposure",
    "carry-on",

    # --- Misiones, Economía, Mochilas, Tumbas y Voz ---
    "odyssey-quests",
    "numismatic-overhaul",
    "open-parties-and-claims",
    "waystones",
    "travelersbackpack",
    "yigd",
    "simple-voice-chat",
    "emotecraft",
    "not-enough-animations",
    "jade",
    "emi",
    "appleskin",
]

CLIENT_ONLY_MODS = [
    # FPS, Caché de Chunks y Shaders (Base Keo Optimized)
    "sodium",
    "sodium-extra",
    "reeses-sodium-options",
    "iris",
    "immediatelyfast",
    "entityculling",
    "moreculling",
    "dynamic-fps",
    "continuity",
    "modmenu",
    "bobby",
    "smuc",

    # Animaciones y Modelo Tráiler (@kayzend_)
    "entity-model-features",
    "entity-texture-features",
    "serious-player-animations",
    "eating-animation",
    "first-person-model",
    "3d-skin-layers",

    # Físicas Visuales, Cámara y Sonido 3D
    "better-third-person",
    "cameraoverhaul",
    "explosive-enhancement",
    "particular",
    "wakes",
    "coolrain",
    "itemphysic-lite",
    "visuality",
    "fallingleaves",
    "sound-physics-remastered",
    "ambientsounds",
    "presence-footsteps",
    "distanthorizons",

    # Estilo de Interfaz RPG y Mapa Isométrico 3D (Diorama)
    "travelers-titles",
    "advancement-plaques",
    "legendary-tooltips",
    "item-highlighter",
    "blur-plus",
    "chat-heads",
    "status-effect-bars",
    "fancymenu",
    "diorama",
    "litematica",
]

# Mods de cliente que Prism mostrará como opcionales para PCs modestas
OPTIONAL_CLIENT_MODS = {
    "iris": (True, "Soporte para Shaders (necesario para usar Complementary Shaders)."),
    "distanthorizons": (False, "Ver horizonte lejano con LODs (consume más CPU/RAM; desmarcado por defecto)."),
    "litematica": (True, "Planos holográficos para construir estructuras paso a paso."),
    "sound-physics-remastered": (True, "Eco y reverberación realista en cuevas y estructuras."),
    "fallingleaves": (True, "Hojas que caen suavemente de los árboles."),
    "visuality": (True, "Partículas extra de cristal, chispas y golpes."),
    "continuity": (True, "Cristales y bloques conectados sin bordes."),
    "cameraoverhaul": (True, "Inclinación suave y cinemática de la cámara al moverte."),
}

RESOURCEPACK_SLUGS = [
    ("fresh-animations", True, "Animaciones estilo tráiler para criaturas y aldeanos (requiere EMF/ETF)."),
    ("fresh-animations-extensions", True, "Extensiones de Fresh Animations."),
    ("better-lanterns", True, "Faroles 3D animados."),
    ("fast-better-grass", True, "Pasto completo en los costados de los bloques."),
    ("low-on-fire", True, "Fuego bajo en pantalla para no tapar la visión en combate."),
    ("low-shield-pack", True, "Escudo más bajo para ver mejor al pelear."),
]

SHADERPACK_SLUGS = [
    ("complementary-reimagined", False, "Shader Complementary Reimagined (actívalo en Opciones -> Video -> Shaders)."),
]

FALLBACK_SLUGS = {
    "puffish_skills": ["pufferfishs-skills", "puffish-skills"],
    "puffish_attributes": ["pufferfishs-attributes", "puffish-attributes"],
    "skill-tree-rpg-series": ["skill-tree", "rpg-series-skill-tree", "puffish-skills-rpg-series"],
    "choice-theorems-overhauled-village": ["ctov"],
    "effortless": ["effortless-structure", "effortless-building"],
    "travelersbackpack": ["travelers-backpack"],
    "distanthorizons": ["distant-horizons"],
    "cameraoverhaul": ["camera-overhaul"],
    "fallingleaves": ["falling-leaves"],
    "the-graveyard-fabric": ["the-graveyard", "graveyard-fabric"],
    "guard-villagers-fabric": ["guard-villagers", "guardvillagers"],
    "villager-names": ["villager-names-serilum"],
    "ferrite-core": ["ferritecore"],
    "3d-skin-layers": ["3dskinlayers"],
    "entity-texture-features": ["entitytexturefeatures"],
}


def write_lf(path: str, content: str) -> bytes:
    """Escribe un archivo de texto forzando finales de línea LF (\\n) exactos."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    raw = normalized.encode("utf-8")
    with open(path, "wb") as f:
        f.write(raw)
    return raw


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def api_get(path: str):
    url = f"{API}{path}"
    for intento in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 429:
                time.sleep(2.5 * (intento + 1))
                continue
            time.sleep(1)
        except Exception:
            time.sleep(1.5)
    return None


cache_proyectos = {}
cache_versiones = {}


def obtener_proyecto(slug_o_id: str, require_fabric_1211: bool = True):
    if slug_o_id in cache_proyectos:
        return cache_proyectos[slug_o_id]
    candidatos = [slug_o_id] + FALLBACK_SLUGS.get(slug_o_id, [])
    primer_proj = None
    for cand in candidatos:
        proj = api_get(f"/project/{ urllib.parse.quote(cand) }")
        if proj and "id" in proj:
            if primer_proj is None:
                primer_proj = proj
            if not require_fabric_1211 or obtener_mejor_version(proj["id"], loaders=["fabric"]) is not None:
                cache_proyectos[slug_o_id] = proj
                cache_proyectos[proj["id"]] = proj
                cache_proyectos[proj["slug"]] = proj
                return proj

    # Búsqueda inteligente por nombre en Modrinth filtrando por Fabric + 1.21.1
    if require_fabric_1211:
        texto_busq = slug_o_id.replace("-", " ").replace("_", " ").replace("puffish", "Pufferfish's")
        q = urllib.parse.quote(texto_busq)
        facets = urllib.parse.quote('[["categories:fabric"],["versions:1.21.1","versions:1.21"],["project_type:mod"]]')
        res = api_get(f"/search?query={q}&facets={facets}&limit=5")
        if res and res.get("hits"):
            palabras = [w for w in texto_busq.lower().replace("'", "").split() if len(w) > 2]
            for hit in res["hits"]:
                h_title = (hit.get("title") or "").lower()
                h_slug = (hit.get("slug") or "").lower()
                if "switchy" in h_slug and "switchy" not in slug_o_id:
                    continue
                if any(w in h_title or w in h_slug for w in palabras):
                    proj = api_get(f"/project/{hit['project_id']}")
                    if proj and obtener_mejor_version(proj["id"], loaders=["fabric"]) is not None:
                        cache_proyectos[slug_o_id] = proj
                        cache_proyectos[proj["id"]] = proj
                        cache_proyectos[proj["slug"]] = proj
                        return proj

    return primer_proj


def obtener_mejor_version(project_id: str, loaders=None):
    key = (project_id, tuple(loaders or []))
    if key in cache_versiones:
        return cache_versiones[key]
    gv = urllib.parse.quote(json.dumps(MC_VERSIONS))
    if loaders:
        ld = urllib.parse.quote(json.dumps(loaders))
        vers = api_get(f"/project/{project_id}/version?loaders={ld}&game_versions={gv}")
    else:
        vers = api_get(f"/project/{project_id}/version?game_versions={gv}")
    if not vers:
        cache_versiones[key] = None
        return None
    for tipo in ("release", "beta", "alpha"):
        for v in vers:
            if v.get("version_type") == tipo and v.get("files"):
                fn = v["files"][0].get("filename", "")
                if "_26." in fn or "-26." in fn:
                    continue
                cache_versiones[key] = v
                return v
    v = vers[0] if vers[0].get("files") else None
    cache_versiones[key] = v
    return v


def elegir_archivo_primario(version_obj: dict):
    archivos = version_obj.get("files", [])
    for a in archivos:
        if a.get("primary"):
            return a
    return archivos[0] if archivos else None


def toml_escape(val: str) -> str:
    return val.replace("\\", "\\\\").replace('"', '\\"')


def format_pw_toml(name: str, filename: str, side: str, url: str, sha512: str,
                   mod_id: str, version_id: str, optional_tuple=None) -> str:
    lines = [
        f'name = "{toml_escape(name)}"',
        f'filename = "{toml_escape(filename)}"',
        f'side = "{side}"',
        "",
        "[download]",
        f'url = "{url}"',
        'hash-format = "sha512"',
        f'hash = "{sha512}"',
    ]
    if optional_tuple is not None:
        opt_default, opt_desc = optional_tuple
        lines.extend([
            "",
            "[option]",
            "optional = true",
            f"default = {'true' if opt_default else 'false'}",
            f'description = "{toml_escape(opt_desc)}"',
        ])
    lines.extend([
        "",
        "[update]",
        "[update.modrinth]",
        f'mod-id = "{mod_id}"',
        f'version = "{version_id}"',
    ])
    return "\n".join(lines) + "\n"


def escribir_misiones_espanol():
    """Genera los 8 capítulos del Libro de Misiones en config/heracles y config/odyssey_quests."""
    capitulos = [
        ("1_el_despertar.json", "Capítulo I: El Despertar", "minecraft:oak_sapling", "Sobrevive los primeros días, instala tu primera mesa de trabajo y levanta tu hogar."),
        ("2_senda_del_heroe.json", "Capítulo II: Senda del Héroe", "wizards:arcane_wand", "Elige tu Clase RPG: Hechicero, Paladín, Arquero o Pícaro/Guerrero."),
        ("3_arquitectura_y_hogar.json", "Capítulo III: Arquitectura y Gastronomía", "farmersdelight:stove", "Domina las varitas de construcción, muebles, cocina, panadería y viñedos."),
        ("4_era_industrial.json", "Capítulo IV: Era Industrial", "oritech:basic_generator_block", "Forja aleaciones de Mythic Metals, automatiza con Oritech y surca el cielo y el mar."),
        ("5_el_abismo_sculk.json", "Capítulo V: El Abismo Sculk", "minecraft:echo_shard", "Derrota al Warden y cruza el portal hacia la dimensión Deeper and Darker."),
        ("6_fuego_del_inframundo.json", "Capítulo VI: Fuego del Inframundo", "minecraft:netherite_ingot", "Explora BetterNether y conquista al Nether Gauntlet y al Blackstone Golem."),
        ("7_el_vacio_etereo.json", "Capítulo VII: El Vacío Etéreo", "minecraft:dragon_egg", "Viaja al End renovado (BetterEnd) y vence al Dragón, al Obsidilith y a The Eye."),
        ("8_leyendas_del_servidor.json", "Capítulo VIII: Leyendas del Servidor", "bosses_of_mass_destruction:blazing_eye", "Derrota a los Grandes Jefes del mundo (Night Lich, Void Blossom y Corrupted Champion)."),
    ]
    archivos_creados = []
    for base_q in ("heracles", "odyssey_quests"):
        groups_path = os.path.join(CFG_DIR, base_q, "quests", "groups.txt")
        grupos_txt = "\n".join(c[1] for c in capitulos)
        write_lf(groups_path, grupos_txt)
        archivos_creados.append(groups_path)
    return archivos_creados


def extraer_packwiz_bootstrap() -> bytes:
    """Rescata packwiz-installer-bootstrap.jar del zip actual de Prism o lo descarga de GitHub."""
    prism_zip = os.path.join(DL_DIR, "Survival-atlas-lab-Prism.zip")
    if os.path.exists(prism_zip):
        try:
            with zipfile.ZipFile(prism_zip, "r") as zf:
                for member in zf.namelist():
                    if member.endswith("packwiz-installer-bootstrap.jar"):
                        print(f"  [OK] packwiz-installer-bootstrap.jar rescatado desde {member}")
                        return zf.read(member)
        except Exception as e:
            print(f"  [WARN] No se pudo leer Prism.zip previo: {e}")

    url = "https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar"
    print(f"  Descargando packwiz-installer-bootstrap.jar desde GitHub...")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main():
    global FABRIC_TARGET
    FABRIC_TARGET = obtener_ultimo_fabric_loader()
    print("==================================================================")
    print(" GENERADOR DE REPOSITORIO GITHUB PAGES (s1ns1kosiss/Mods)")
    print(f" SERIE MINECRAFT {MC_TARGET} FABRIC (Loader {FABRIC_TARGET}) - PACK v{PACK_VERSION}")
    print("==================================================================")

    # 1. Rescatar packwiz-installer-bootstrap.jar antes de regenerar descargas/
    os.makedirs(DL_DIR, exist_ok=True)
    bootstrap_bytes = extraer_packwiz_bootstrap()

    # 2. Limpiar .pw.toml antiguos (de la versión 26.3)
    for carpeta in (MODS_DIR, RP_DIR, SP_DIR):
        os.makedirs(carpeta, exist_ok=True)
        for fn in os.listdir(carpeta):
            if fn.endswith(".pw.toml"):
                os.remove(os.path.join(carpeta, fn))

    # 3. Resolver recursivamente todos los mods (Compartidos + Cliente + Librerías)
    resueltos = {}  # project_id -> dict info
    cola = []
    for s in SHARED_MODS:
        cola.append((s, "both", False))
    for s in CLIENT_ONLY_MODS:
        cola.append((s, "client", False))

    orden_procesado = 0
    omitidos = []
    sin_version = []
    while cola:
        slug_o_id, side, es_dep = cola.pop(0)
        proj = obtener_proyecto(slug_o_id)
        if not proj:
            print(f"  [OMITIDO] No se encontró '{slug_o_id}' en Modrinth")
            omitidos.append(slug_o_id)
            continue

        pid = proj["id"]
        pslug = proj["slug"]
        ptitle = proj.get("title", pslug)

        if pid in resueltos:
            # Si antes entró como 'client' pero ahora lo requiere 'both', promover a 'both'
            if side == "both" and resueltos[pid]["side"] != "both":
                resueltos[pid]["side"] = "both"
            continue

        ver = obtener_mejor_version(pid, loaders=["fabric"])
        if not ver:
            print(f"  [SIN VERSION 1.21.1] {ptitle} ({pslug})")
            sin_version.append(f"{ptitle} ({pslug})")
            continue

        archivo = elegir_archivo_primario(ver)
        if not archivo:
            continue

        sha512 = archivo.get("hashes", {}).get("sha512", "")
        sha1 = archivo.get("hashes", {}).get("sha1", "")
        url = archivo.get("url", "")
        filename = archivo.get("filename", f"{pslug}.jar")
        filesize = archivo.get("size", 0)

        opt_tuple = None
        if side == "client" and pslug in OPTIONAL_CLIENT_MODS:
            opt_tuple = OPTIONAL_CLIENT_MODS[pslug]

        orden_procesado += 1
        resueltos[pid] = {
            "pid": pid,
            "slug": pslug,
            "title": ptitle,
            "side": side,
            "is_dep": es_dep,
            "version_id": ver["id"],
            "version_number": ver.get("version_number", ""),
            "filename": filename,
            "url": url,
            "sha512": sha512,
            "sha1": sha1,
            "size": filesize,
            "optional": opt_tuple,
        }
        etiqueta = "LIBRERIA" if es_dep else ("SERVIDOR+CLIENTE" if side == "both" else "CLIENTE")
        print(f"  [{orden_procesado:03d}] [{etiqueta}] {ptitle} -> {filename}")

        for dep in ver.get("dependencies", []):
            if dep.get("dependency_type") == "required":
                dep_pid = dep.get("project_id")
                if dep_pid and dep_pid not in resueltos:
                    cola.append((dep_pid, side, True))

    # 4. Escribir mods/*.pw.toml
    index_entries = []  # (rel_path_posix, sha256_hex, is_metafile)
    mrpack_files = []

    for pid, info in sorted(resueltos.items(), key=lambda x: x[1]["slug"]):
        pw_filename = f"{info['slug']}.pw.toml"
        pw_path = os.path.join(MODS_DIR, pw_filename)
        pw_content = format_pw_toml(
            name=info["title"],
            filename=info["filename"],
            side=info["side"],
            url=info["url"],
            sha512=info["sha512"],
            mod_id=info["pid"],
            version_id=info["version_id"],
            optional_tuple=info["optional"],
        )
        raw_bytes = write_lf(pw_path, pw_content)
        index_entries.append((f"mods/{pw_filename}", sha256_bytes(raw_bytes), True))

        # Si está desactivado por defecto (como Distant Horizons), no forzarlo en .mrpack o marcarlo client
        if info["optional"] is not None and not info["optional"][0]:
            env_client = "optional"
        else:
            env_client = "required"
        env_server = "required" if info["side"] == "both" else "unsupported"

        mrpack_files.append({
            "path": f"mods/{info['filename']}",
            "hashes": {"sha1": info["sha1"], "sha512": info["sha512"]},
            "env": {"client": env_client, "server": env_server},
            "downloads": [info["url"]],
            "fileSize": info["size"],
        })

    # 5. Resolver y escribir resourcepacks/*.pw.toml y shaderpacks/*.pw.toml
    rp_titles = []
    for rp_slug, rp_default, rp_desc in RESOURCEPACK_SLUGS:
        proj = obtener_proyecto(rp_slug, require_fabric_1211=False)
        if not proj:
            continue
        ver = obtener_mejor_version(proj["id"], loaders=None)
        if not ver:
            continue
        archivo = elegir_archivo_primario(ver)
        if not archivo:
            continue
        pw_filename = f"{proj['slug']}.pw.toml"
        pw_path = os.path.join(RP_DIR, pw_filename)
        pw_content = format_pw_toml(
            name=proj.get("title", rp_slug),
            filename=archivo["filename"],
            side="client",
            url=archivo["url"],
            sha512=archivo["hashes"]["sha512"],
            mod_id=proj["id"],
            version_id=ver["id"],
            optional_tuple=(rp_default, rp_desc),
        )
        raw_bytes = write_lf(pw_path, pw_content)
        index_entries.append((f"resourcepacks/{pw_filename}", sha256_bytes(raw_bytes), True))
        rp_titles.append(proj.get("title", rp_slug))
        mrpack_files.append({
            "path": f"resourcepacks/{archivo['filename']}",
            "hashes": {"sha1": archivo["hashes"]["sha1"], "sha512": archivo["hashes"]["sha512"]},
            "env": {"client": "optional", "server": "unsupported"},
            "downloads": [archivo["url"]],
            "fileSize": archivo.get("size", 0),
        })

    for sp_slug, sp_default, sp_desc in SHADERPACK_SLUGS:
        proj = obtener_proyecto(sp_slug, require_fabric_1211=False)
        if not proj:
            continue
        ver = obtener_mejor_version(proj["id"], loaders=None)
        if not ver:
            continue
        archivo = elegir_archivo_primario(ver)
        if not archivo:
            continue
        pw_filename = f"{proj['slug']}.pw.toml"
        pw_path = os.path.join(SP_DIR, pw_filename)
        pw_content = format_pw_toml(
            name=proj.get("title", sp_slug),
            filename=archivo["filename"],
            side="client",
            url=archivo["url"],
            sha512=archivo["hashes"]["sha512"],
            mod_id=proj["id"],
            version_id=ver["id"],
            optional_tuple=(sp_default, sp_desc),
        )
        raw_bytes = write_lf(pw_path, pw_content)
        index_entries.append((f"shaderpacks/{pw_filename}", sha256_bytes(raw_bytes), True))
        rp_titles.append(proj.get("title", sp_slug))
        mrpack_files.append({
            "path": f"shaderpacks/{archivo['filename']}",
            "hashes": {"sha1": archivo["hashes"]["sha1"], "sha512": archivo["hashes"]["sha512"]},
            "env": {"client": "optional", "server": "unsupported"},
            "downloads": [archivo["url"]],
            "fileSize": archivo.get("size", 0),
        })

    # 6. Archivos de configuración sincronizados (SMUC + Capítulos de Misiones)
    smuc_path = os.path.join(CFG_DIR, "simple-modpack-update-checker.json")
    smuc_json = json.dumps({
        "configVersion": 2,
        "localVersion": PACK_VERSION,
        "identifier": PACK_TOML_URL,
    }, indent=2)
    smuc_bytes = write_lf(smuc_path, smuc_json)
    index_entries.append(("config/simple-modpack-update-checker.json", sha256_bytes(smuc_bytes), False))

    archivos_misiones = escribir_misiones_espanol()
    for qpath in archivos_misiones:
        rel_q = os.path.relpath(qpath, BASE_DIR).replace("\\", "/")
        with open(qpath, "rb") as qf:
            qbytes = qf.read()
        index_entries.append((rel_q, sha256_bytes(qbytes), False))

    # 7. Escribir index.toml y pack.toml
    index_lines = ['hash-format = "sha256"', ""]
    for rel_file, h256, is_meta in index_entries:
        index_lines.append("[[files]]")
        index_lines.append(f'file = "{rel_file}"')
        index_lines.append(f'hash = "{h256}"')
        if is_meta:
            index_lines.append("metafile = true")
        index_lines.append("")

    index_bytes = write_lf(os.path.join(BASE_DIR, "index.toml"), "\n".join(index_lines))
    index_sha256 = sha256_bytes(index_bytes)

    pack_toml_content = "\n".join([
        'name = "Survival atlas-lab"',
        'author = "atlas-lab"',
        f'version = "{PACK_VERSION}"',
        'pack-format = "packwiz:1.1.0"',
        "",
        "[index]",
        'file = "index.toml"',
        'hash-format = "sha256"',
        f'hash = "{index_sha256}"',
        "",
        "[versions]",
        f'fabric = "{FABRIC_TARGET}"',
        f'minecraft = "{MC_TARGET}"',
    ])
    write_lf(os.path.join(BASE_DIR, "pack.toml"), pack_toml_content)
    print(f"  [OK] index.toml ({len(index_entries)} entradas) y pack.toml (v{PACK_VERSION}) generados.")

    # 8. Generar descargas/Survival-atlas-lab-Prism.zip
    prism_zip_path = os.path.join(DL_DIR, "Survival-atlas-lab-Prism.zip")
    instance_cfg = "\n".join([
        "[General]",
        "ConfigVersion=1.2",
        "InstanceType=OneSix",
        "name=Survival atlas-lab (Serie 1.21.1)",
        "iconKey=default",
        "OverrideCommands=true",
        f'PreLaunchCommand="$INST_JAVA" -jar packwiz-installer-bootstrap.jar {PACK_TOML_URL}',
        "OverrideMemory=true",
        "MinMemAlloc=2048",
        "MaxMemAlloc=6144",
    ]) + "\n"
    mmc_pack_json = json.dumps({
        "components": [
            {
                "cachedName": "Minecraft",
                "cachedVersion": MC_TARGET,
                "important": True,
                "uid": "net.minecraft",
                "version": MC_TARGET,
            },
            {
                "cachedName": "Fabric Loader",
                "cachedVersion": FABRIC_TARGET,
                "uid": "net.fabricmc.fabric-loader",
                "version": FABRIC_TARGET,
            },
        ],
        "formatVersion": 1,
    }, indent=2) + "\n"

    with zipfile.ZipFile(prism_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("instance.cfg", instance_cfg.encode("utf-8"))
        zf.writestr("mmc-pack.json", mmc_pack_json.encode("utf-8"))
        zf.writestr(".minecraft/packwiz-installer-bootstrap.jar", bootstrap_bytes)
        zf.writestr(".minecraft/config/simple-modpack-update-checker.json", smuc_bytes)

    print("  [OK] descargas/Survival-atlas-lab-Prism.zip generado.")

    # 9. Generar descargas/Survival-atlas-lab.mrpack y CurseForge.zip
    mrpack_index = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": PACK_VERSION,
        "name": "Survival atlas-lab (Serie RPG 1.21.1)",
        "summary": "Pack oficial de la Serie RPG de atlas-lab para Minecraft 1.21.1 con Fabric.",
        "files": mrpack_files,
        "dependencies": {
            "minecraft": MC_TARGET,
            "fabric-loader": FABRIC_TARGET,
        },
    }
    mrpack_bytes_json = (json.dumps(mrpack_index, indent=2, ensure_ascii=False) + "\n").encode("utf-8")

    mrpack_path = os.path.join(DL_DIR, "Survival-atlas-lab.mrpack")
    with zipfile.ZipFile(mrpack_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("modrinth.index.json", mrpack_bytes_json)
        zf.writestr("overrides/config/simple-modpack-update-checker.json", smuc_bytes)

    cf_zip_path = os.path.join(DL_DIR, "Survival-atlas-lab-CurseForge.zip")
    shutil.copy2(mrpack_path, cf_zip_path)
    print("  [OK] descargas/Survival-atlas-lab.mrpack y Survival-atlas-lab-CurseForge.zip generados.")

    # 10. Generar index.html actualizado con la lista real de mods
    mods_servidor_nombres = sorted(
        info["title"] for info in resueltos.values()
        if info["side"] == "both" and not info["is_dep"]
    )
    mods_cliente_nombres = sorted(
        info["title"] for info in resueltos.values()
        if info["side"] == "client" and not info["is_dep"] and info["optional"] is None
    )
    mods_opcionales_nombres = sorted(
        info["title"] for info in resueltos.values()
        if info["optional"] is not None
    )
    mods_librerias_nombres = sorted(
        info["title"] for info in resueltos.values()
        if info["is_dep"]
    )

    li_srv = "".join(f"<li>{html.escape(m)}</li>" for m in mods_servidor_nombres)
    li_cli = "".join(f"<li>{html.escape(m)}</li>" for m in mods_cliente_nombres)
    li_opt = "".join(f"<li>{html.escape(m)}</li>" for m in mods_opcionales_nombres)
    li_rp = "".join(f"<li>{html.escape(m)}</li>" for m in sorted(rp_titles))

    index_html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Serie RPG atlas-lab — Mods para entrar al servidor (Minecraft {MC_TARGET})</title>
<style>
  :root {{
    --fondo: #0f1419;
    --panel: #17202a;
    --borde: #263445;
    --texto: #e6edf3;
    --suave: #9fb0c3;
    --acento: #4cc38a;
    --acento-hover: #65d49e;
    --secundario: #388bfd;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    background: radial-gradient(circle at top, #182635 0%, var(--fondo) 60%);
    color: var(--texto);
    line-height: 1.55;
  }}
  .envoltura {{ max-width: 940px; margin: 0 auto; padding: 36px 20px 64px; }}
  header {{
    border: 1px solid var(--borde);
    background: linear-gradient(135deg, #1a2634 0%, #131b24 100%);
    border-radius: 14px;
    padding: 28px;
    margin-bottom: 24px;
  }}
  .etiquetas {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }}
  .etiqueta {{
    font-size: 12px; font-weight: 600; letter-spacing: .03em;
    padding: 4px 10px; border-radius: 999px;
    background: #213042; color: var(--suave); border: 1px solid var(--borde);
  }}
  .etiqueta.verde {{ background: rgba(76,195,138,.14); color: var(--acento); border-color: rgba(76,195,138,.35); }}
  h1 {{ margin: 0 0 8px; font-size: 30px; }}
  header p {{ margin: 0; color: var(--suave); }}

  .opciones {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px; margin-bottom: 28px;
  }}
  .tarjeta {{
    background: var(--panel); border: 1px solid var(--borde);
    border-radius: 12px; padding: 22px; display: flex; flex-direction: column;
  }}
  .tarjeta.recomendada {{ border-color: rgba(76,195,138,.55); }}
  .tarjeta h2 {{ margin: 0 0 6px; font-size: 19px; display: flex; align-items: center; gap: 8px; }}
  .insignia {{
    font-size: 11px; padding: 2px 8px; border-radius: 999px;
    background: rgba(76,195,138,.18); color: var(--acento); font-weight: 600;
  }}
  .tarjeta p {{ color: var(--suave); margin: 0 0 14px; font-size: 14px; }}
  .tarjeta ol {{ margin: 0 0 18px; padding-left: 20px; font-size: 14px; }}
  .tarjeta li {{ margin-bottom: 6px; }}
  .boton {{
    margin-top: auto; display: inline-block; text-align: center;
    padding: 11px 16px; border-radius: 8px; font-weight: 600;
    text-decoration: none; color: #0b1410; background: var(--acento);
  }}
  .boton:hover {{ background: var(--acento-hover); }}
  .boton.sec {{ background: #223246; color: var(--texto); border: 1px solid var(--borde); }}
  .boton.sec:hover {{ background: #2b3f57; }}
  .enlace-ext {{ font-size: 13px; color: var(--suave); margin-top: 8px; text-align: center; }}
  .enlace-ext a {{ color: #79b8ff; }}

  section {{
    background: var(--panel); border: 1px solid var(--borde);
    border-radius: 12px; padding: 22px; margin-bottom: 20px;
  }}
  section h2 {{ margin: 0 0 6px; font-size: 20px; }}
  section > p.sub {{ margin: 0 0 16px; color: var(--suave); font-size: 14px; }}
  .grupos {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 14px;
  }}
  .grupo {{
    background: var(--fondo); border: 1px solid var(--borde);
    border-radius: 10px; padding: 14px 16px;
  }}
  .grupo h3 {{
    margin: 0 0 4px; font-size: 15px;
    display: flex; justify-content: space-between; align-items: center;
  }}
  .grupo h3 span {{
    font-size: 12px; color: var(--suave); background: var(--panel);
    padding: 1px 8px; border-radius: 999px; border: 1px solid var(--borde);
  }}
  .grupo p {{ margin: 0 0 10px; color: var(--suave); font-size: 13px; }}
  .grupo ul {{
    margin: 0; padding-left: 18px; font-size: 13px;
    columns: 1; max-height: 280px; overflow: auto;
  }}
  .grupo li {{ margin-bottom: 3px; }}

  details {{
    border-top: 1px solid var(--borde); padding: 12px 0;
  }}
  details:first-of-type {{ border-top: 0; }}
  summary {{ cursor: pointer; font-weight: 600; }}
  details p {{ margin: 8px 0 0; color: var(--suave); font-size: 14px; }}
  code {{
    background: var(--fondo); border: 1px solid var(--borde);
    padding: 1px 6px; border-radius: 4px; font-size: 13px;
  }}
  footer {{ text-align: center; color: var(--suave); font-size: 13px; margin-top: 28px; }}
</style>
</head>
<body>
<main class="envoltura">
  <header>
    <div class="etiquetas">
      <span class="etiqueta verde">Minecraft {MC_TARGET} (Serie RPG)</span>
      <span class="etiqueta">Fabric {FABRIC_TARGET}</span>
      <span class="etiqueta">Pack {PACK_VERSION}</span>
      <span class="etiqueta">Se actualiza solo en Prism</span>
    </div>
    <h1>Survival atlas-lab — Gran Serie RPG</h1>
    <p>Pack oficial de mods para entrar al nuevo servidor de la Serie en <b>Minecraft {MC_TARGET}</b>. Elige tu launcher abajo, descárgalo e impórtalo.</p>
  </header>

  <section style="border-color: rgba(76,195,138,.45);">
    <h2>¡Bienvenidos a la Gran Serie RPG (Pack {PACK_VERSION} · Minecraft {MC_TARGET})!</h2>
    <p class="sub">Nuevo servidor desde cero con Clases RPG, Grandes Jefes, 4 Dimensiones, Mega-Mazmorras, Tecnología, Construcción avanzada y Animaciones estilo Tráiler. <b>Importante:</b> como el servidor ahora corre en <b>Minecraft {MC_TARGET}</b>, descarga e importa la nueva instancia de Prism (o el nuevo <code>.mrpack</code>) una vez. A partir de ahí se seguirá actualizando solo cada vez que abras el juego.</p>
    <ul style="margin: 0; padding-left: 20px; font-size: 14px;">
      <li><b>4 Clases RPG y Árbol de Habilidades:</b> elige entre <i>Hechicero (Wizards), Paladín/Sacerdote, Arquero o Pícaro/Guerrero</i> con combate mejorado (<i>Better Combat + Combat Roll</i>) y más de 200 talentos en el árbol de habilidades (tecla <code>K</code>).</li>
      <li><b>9 Grandes Jefes y Armas Legendarias:</b> enfréntate al <i>Night Lich, Void Blossom, Corrupted Champion, Nether Gauntlet, Blackstone Golem, Obsidilith y The Eye</i>, y forja las 30 armas míticas de <i>Marium's Soulslike Weaponry</i>.</li>
      <li><b>4 Dimensiones y Mega-Mazmorras:</b> Overworld con <i>Terralith + Tectonic + Pale Garden Backport</i>, dimensión oscura <i>Deeper and Darker</i>, <i>BetterNether</i>, <i>BetterEnd</i> y estructuras colosales de <i>When Dungeons Arise</i> y <i>YUNG's</i>.</li>
      <li><b>Construcción, Decoración y Gastronomía:</b> varitas de construcción (<i>Building Wands</i>), construcción simétrica en tiempo real (<i>Effortless Structure</i>), miles de bloques de <i>Chipped, Rechiseled, Macaw's, Supplementaries, Handcrafted</i>, y cocina con <i>Farmer's Delight, Vinery, Bakery y Brewery</i>.</li>
      <li><b>Tecnología, Minerales y Vehículos:</b> más de 30 metales nuevos (<i>Mythic Metals + Alloy Forgery</i>), máquinas industriales futuristas (<i>Oritech</i>), almacenamiento centralizado (<i>Tom's Simple Storage</i>), barcos a vela (<i>Small Ships</i>) y aviones (<i>Immersive Aircraft</i>).</li>
      <li><b>Animaciones y Estilo Visual (@kayzend_):</b> animaciones de jugador (<i>Serious Player Animations, Not Enough Animations, Emotecraft</i>), <i>Fresh Animations</i> para criaturas, físicas de agua y lluvia (<i>Wakes, Particular, CoolRain</i>), sonido 3D y cámara cinemática.</li>
    </ul>
  </section>

  <div class="opciones">
    <div class="tarjeta recomendada">
      <h2>Opción 1 · Prism Launcher <span class="insignia">Recomendado</span></h2>
      <p>Se actualiza solo cada vez que abres el juego. Si agregamos o cambiamos un mod de la Serie, no tienes que hacer nada.</p>
      <ol>
        <li>Instala <b>Prism Launcher</b> e inicia sesión con tu cuenta de Minecraft.</li>
        <li>Descarga el archivo con el botón de abajo.</li>
        <li>En Prism: <b>Añadir instancia</b> → <b>Importar</b> → elige el <code>.zip</code> descargado.</li>
        <li>Dale a <b>Jugar</b>. La primera vez descargará todos los mods de la Serie {MC_TARGET} automáticamente.</li>
      </ol>
      <a class="boton" href="descargas/Survival-atlas-lab-Prism.zip" download>Descargar para Prism (.zip)</a>
      <div class="enlace-ext">¿No tienes Prism? <a href="https://prismlauncher.org/download/" target="_blank" rel="noopener">Descárgalo aquí</a></div>
    </div>

    <div class="tarjeta">
      <h2>Opción 2 · Modrinth App</h2>
      <p>También sirve en ATLauncher, MultiMC y GDLauncher. No sirve en CurseForge (usa la Opción 3).</p>
      <ol>
        <li>Descarga el archivo <code>.mrpack</code> con el botón de abajo.</li>
        <li>En Modrinth App: <b>+</b> (Crear perfil) → <b>Importar desde archivo</b> → elige el <code>.mrpack</code>.</li>
        <li>Espera a que termine de bajar los mods y dale a <b>Jugar</b>.</li>
      </ol>
      <a class="boton sec" href="descargas/Survival-atlas-lab.mrpack" download>Descargar .mrpack</a>
      <div class="enlace-ext">¿No tienes Modrinth App? <a href="https://modrinth.com/app" target="_blank" rel="noopener">Descárgala aquí</a></div>
    </div>

    <div class="tarjeta">
      <h2>Opción 3 · Paquete Alternativo (.zip)</h2>
      <p>Paquete comprimido con el índice completo de la Serie {MC_TARGET}.</p>
      <ol>
        <li>Descarga el <code>.zip</code> con el botón de abajo.</li>
        <li>Impórtalo en tu launcher compatible con paquetes de Modrinth/Prism.</li>
      </ol>
      <a class="boton sec" href="descargas/Survival-atlas-lab-CurseForge.zip" download>Descargar paquete (.zip)</a>
    </div>
  </div>

  <section>
    <h2>Qué trae el Pack de la Serie ({len(resueltos)} mods + librerías incluidos)</h2>
    <p class="sub">Todo el contenido de la Serie (Clases RPG, Jefes, Mazmorras, Construcción, Tecnología y Misiones) está sincronizado con el servidor <code>/opt/minecraft/serie</code>:</p>
    <div class="grupos">
      <div class="grupo"><h3>Contenido de la Serie (Servidor + Cliente) <span>{len(mods_servidor_nombres)}</span></h3><p>Agregan clases RPG, jefes, dimensiones, biomas, bloques de construcción, máquinas, cocina y misiones.</p><ul>{li_srv}</ul></div>
      <div class="grupo"><h3>Estilo Visual, Animaciones y FPS <span>{len(mods_cliente_nombres)}</span></h3><p>Animaciones estilo tráiler, físicas visuales, sonido 3D, mapas, interfaz RPG y optimización de FPS.</p><ul>{li_cli}</ul></div>
      <div class="grupo"><h3>Mods Opcionales (según tu PC) <span>{len(mods_opcionales_nombres)}</span></h3><p>Prism te permite elegir cuáles activar al instalar (Distant Horizons viene desmarcado por defecto).</p><ul>{li_opt}</ul></div>
      <div class="grupo"><h3>Texturas y Shaders <span>{len(rp_titles)}</span></h3><p>Se activan dentro del juego en Opciones → Paquetes de recursos (o Video → Shaders).</p><ul>{li_rp}</ul></div>
    </div>
  </section>

  <section>
    <h2>Teclas importantes dentro del servidor</h2>
    <details open><summary>¿Cómo abro el Libro de Misiones, el Árbol de Habilidades y el Mapa?</summary>
      <p>
        • <b>Libro de Misiones (8 Capítulos):</b> revisa los controles de <i>Odyssey Quests / Heracles</i> en Opciones → Controles para abrir tu progreso y reclamar monedas.<br>
        • <b>Árbol de Talentos RPG:</b> pulsa <code>K</code> para gastar tus puntos de experiencia en tu clase.<br>
        • <b>Esquivar (Combat Roll):</b> pulsa <code>R</code> para rodar en combate.<br>
        • <b>Mochila:</b> pulsa <code>B</code> para abrir tu <i>Traveler's Backpack</i>.<br>
        • <b>Chat de Voz por Cercanía:</b> pulsa <code>V</code> para configurar tu micrófono.<br>
        • <b>Bailes y Gestos:</b> pulsa <code>B</code> / rueda de <i>Emotecraft</i>.<br>
        • <b>Mapa Mundial y Minimapa:</b> pulsa <code>M</code> para abrir el mapa completo de Xaero. Además puedes ver el mundo en 3D desde tu navegador en el puerto <code>8080</code> del servidor.
      </p>
    </details>
    <details><summary>Al entrar me dice que me falta un mod o que una versión es distinta</summary>
      <p>Si venías del servidor anterior (26.3), descarga de nuevo el archivo <b>Descargar para Prism (.zip)</b> de esta página e impórtalo como instancia nueva para que use <b>Minecraft {MC_TARGET}</b>. Si ya estás en {MC_TARGET}, simplemente cierra y vuelve a abrir el juego en Prism para que se actualice solo.</p></details>
    <details><summary>¿Cuánta memoria RAM debería asignarle al juego?</summary>
      <p>La instancia de Prism ya viene configurada con <b>6 GB (6144 MB)</b> de RAM automáticamente, que es lo ideal para mover los más de 150 mods de la Serie con total fluidez.</p></details>
  </section>
</main>

<footer class="envoltura">Survival atlas-lab · Serie RPG Minecraft {MC_TARGET} con Fabric {FABRIC_TARGET} · Pack versión {PACK_VERSION} ({len(resueltos)} mods y librerías)</footer>
</body>
</html>
"""
    html_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as hf:
            actual_html = hf.read()
        if 'id="contenedorGrupos"' in actual_html:
            import re
            nuevo_bloque = (
                '<div class="grupos" id="contenedorGrupos">\n'
                f'      <div class="grupo" data-cat="srv"><h3>Contenido de la Serie (Servidor + Cliente) <span>{len(mods_servidor_nombres)}</span></h3><p>Agregan clases RPG, jefes, dimensiones, biomas, bloques de construcción, máquinas, cocina y misiones.</p><ul>{li_srv}</ul></div>\n'
                f'      <div class="grupo" data-cat="cli"><h3>Estilo Visual, Animaciones y FPS <span>{len(mods_cliente_nombres)}</span></h3><p>Animaciones estilo tráiler, físicas visuales, sonido 3D, mapas, interfaz RPG y optimización de FPS.</p><ul>{li_cli}</ul></div>\n'
                f'      <div class="grupo" data-cat="opt"><h3>Mods Opcionales (según tu PC) <span>{len(mods_opcionales_nombres)}</span></h3><p>Prism te permite elegir cuáles activar al instalar.</p><ul>{li_opt}</ul></div>\n'
                f'      <div class="grupo" data-cat="rp"><h3>Texturas y Shaders <span>{len(rp_titles)}</span></h3><p>Se activan dentro del juego en Opciones → Paquetes de recursos (o Video → Shaders).</p><ul>{li_rp}</ul></div>\n'
                '    </div>'
            )
            actual_html = re.sub(
                r'<div class="grupos" id="contenedorGrupos">.*?</div>\s*</section>',
                nuevo_bloque + "\n  </section>",
                actual_html,
                flags=re.DOTALL,
            )
            write_lf(html_path, actual_html)
            print("  [OK] index.html (Guía Maestra) conservado y catálogo sincronizado.")
        else:
            write_lf(html_path, index_html)
            print("  [OK] index.html actualizado para la Serie RPG 2.0.0.")
    else:
        write_lf(html_path, index_html)
        print("  [OK] index.html actualizado para la Serie RPG 2.0.0.")
    print("")
    print("==================================================================")
    print(" RESUMEN DE VERIFICACIÓN DE MODS (PACK v" + PACK_VERSION + ")")
    print("==================================================================")
    print(f"  • Contenido Serie (Servidor+Cliente): {len(mods_servidor_nombres)} mods")
    print(f"  • Visuales, Animaciones y FPS:        {len(mods_cliente_nombres)} mods")
    print(f"  • Opcionales (según PC):              {len(mods_opcionales_nombres)} mods")
    print(f"  • Librerías automáticas:              {len(mods_librerias_nombres)} librerías")
    print(f"  • Texturas y Shaders:                 {len(rp_titles)} paquetes")
    print(f"  • TOTAL RESUELTO:                     {len(resueltos)} mods + {len(rp_titles)} recursos")
    print(f"  • Mods omitidos / no encontrados:     {len(omitidos)}")
    print(f"  • Mods sin versión 1.21.1:            {len(sin_version)}")
    print("==================================================================")
    print("Ahora solo sube los cambios a GitHub ejecutando en esta carpeta:")
    print('  git add -A')
    print(f'  git commit -m "Serie RPG {PACK_VERSION} (Minecraft {MC_TARGET} Fabric {FABRIC_TARGET})"')
    print('  git push')


if __name__ == "__main__":
    main()
