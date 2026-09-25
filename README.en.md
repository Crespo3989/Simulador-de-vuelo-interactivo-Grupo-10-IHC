# AeroGlobo 3D · Navigation Lab

*[Leer en español](README.md)*

An air-route simulator on an interactive 3D globe, built with **Python**, **Tkinter**, **NumPy** and **Pillow**. It lets you compare an **automatic** flight (which follows the great circle, the shortest route on the sphere) with a **manual** flight you steer with the keyboard, on the same route.

> This is an educational spherical-geometry tool, not a physics-based flight simulator. The speed is deliberately accelerated (950 km per simulation second).

> **Note:** the application interface is in Spanish. This guide shows the button labels exactly as they appear on screen, with their English meaning in parentheses.

---

## Features

- **3D globe with orthographic projection**: rendered pixel by pixel from spherical coordinates, with lighting and an atmospheric halo. The far side of the globe is hidden.
- **Real cartography**: continent outlines come from Natural Earth (1:110m, public domain).
- **74 cities** across every continent, using approximate city-centre coordinates (not airports).
- **Routes with stopovers**: an origin, up to 5 stopovers and a destination.
- **Two flight modes**:
  - **Automatic**: the plane follows the great-circle arc between each pair of destinations.
  - **Manual**: you fly it with WASD or the arrow keys.
- **Live metrics**: elapsed time, distance flown and distance to the next destination.
- **Comparison** between the two modes and **CSV export**.
- Optional meridian and parallel grid, and a camera that can follow the plane.

---

## Requirements

- Python 3.10 or newer
- Tkinter (included with the official Python installer on Windows; on Linux, install `python3-tk`)
- NumPy ≥ 1.24
- Pillow ≥ 9.1

You only need an Internet connection to install the dependencies the first time. The program uses no API keys and does not connect to the Internet while it runs.

---

## Installation and running

From the project folder:

```bash
python -m pip install -r requirements.txt
```

```bash
python globo_aereo.py
```

On Windows you can also use:

```bash
py globo_aereo.py
```

On Linux (Debian/Ubuntu), if Tkinter is missing:

```bash
sudo apt install python3-tk
```

---

## Project structure

```
aeroglobo_3d/
├── globo_aereo.py        # Main application: UI, camera, routes and flight logic
├── tierra_color.py       # Builds the planet texture and renders it onto the sphere
├── continentes.geojson   # Continent outlines (Natural Earth)
├── requirements.txt      # Python dependencies
├── README.md             # Documentation in Spanish
├── README.en.md          # Documentation in English
└── LEEME_GLOBO.txt       # Original project notes (Spanish)
```

`continentes.geojson` and `tierra_color.py` must be in the same folder as `globo_aereo.py`. If the GeoJSON file is missing, the application shows an error on startup.

---

## How to use it

### 1. Plan the route
1. Under **Origen** (Origin), choose the departure city.
2. To add a stopover, pick a city under **Destino / siguiente escala** (Destination / next stopover) and click **+ Escala** (+ Stopover). Repeat for each stopover, up to 5.
3. Choose the final destination under **Destino / siguiente escala**.
4. **Limpiar** (Clear) removes all stopovers.

The panel shows the route and its **minimum distance** (*Ruta mínima*), which is the sum of the great-circle arcs.

### 2. Fly
- **Volar automático** (Fly automatic): the plane flies the optimal route on its own.
- **Volar manual** (Fly manual): you fly the plane yourself and must reach each destination in order.

You can't edit the route during a flight. If you start another flight, the program asks you to confirm before discarding the current one.

### 3. Compare and export
- **Comparar resultados** (Compare results): shows the time and distance difference between the manual and automatic modes. You must complete both modes on exactly the same route.
- **Exportar resultados CSV** (Export results to CSV): saves every result from the session.

---

## Controls

| Action | Control |
|---|---|
| Rotate the globe | Drag with the mouse (turns off camera follow) |
| Zoom in / out | Mouse wheel |
| North | `W` or `↑` |
| South | `S` or `↓` |
| West | `A` or `←` |
| East | `D` or `→` |
| Pause / resume | `Space` or the **Pausar / continuar** button |

You can combine keys to fly diagonally; the speed stays the same. Directions are **geographic** (north, south, east, west), not relative to the screen, so they don't change when you rotate the camera.

Checkboxes in the side panel:
- **Mostrar meridianos y paralelos**: show meridians and parallels.
- **Cámara sigue al avión**: camera follows the plane.

---

## Model and measurement

| Parameter | Value |
|---|---|
| Earth radius | 6,371 km (perfect sphere) |
| Speed (both modes) | 950 km per simulation second |
| Arrival radius | 65 km from the city centre |
| Maximum time step per frame | 0.08 s |
| Update rate | ~30 fps |

- Distances are computed as arcs on the sphere: `d = R · acos(a · b)`, where `a` and `b` are unit vectors.
- Automatic mode follows great circles between consecutive destinations.
- Once the plane is within 65 km of a city, the remaining distance to the city centre is added. Both modes use the same rule.
- Time only counts while a flight is active; pauses are not included.
- There are no collisions, wind, fuel or obstacles.

### CSV format

Example with approximate values:

```csv
ruta,modo,segundos_simulacion,km_esfera
"Quito, Ecuador → Madrid, España",Automático,9.2,8737.99
```

| Column | Meaning |
|---|---|
| `ruta` | Route, cities in order |
| `modo` | Mode: `Automático` or `Manual` |
| `segundos_simulacion` | Simulation seconds |
| `km_esfera` | Kilometres flown on the sphere |

The file is saved as UTF-8 with a BOM so that Excel displays accented characters correctly. Only the latest result for each route and mode is kept during a session, so export before closing if you want to keep your results.

---

## Technical details

- **Globe rendering** (`tierra_color.py`): on startup, the GeoJSON polygons are rasterised into a 2048×1024 equirectangular texture with stylised colours (ocean, coastlines, land and polar ice). Each frame, a reverse ray is cast from every pixel onto the sphere to find its latitude and longitude, and the colour is sampled from the texture. The internal resolution is capped at 560 px so it stays smooth on modest hardware.
- **Lines on the globe** (routes, flight trail and grid): projected in 3D and clipped exactly at the horizon, so no segments from the hidden hemisphere appear.
- **Spherical geometry** (`globo_aereo.py`): unit vectors, the tangent vector toward the destination, movement along a great circle and arc interpolation. Antipodal points and the poles are handled as special cases.

---

## Limitations

- The planet's colours are decorative. They don't represent climate, terrain or ocean depth.
- Lighting is fixed relative to the camera; there is no day/night simulation.
- Cities are approximate urban centres, not airports.
- Times are accelerated and can't be used to estimate real flight durations.
- The automatic mode is geometric and deterministic; it is not artificial intelligence.
- This is not a substitute for real aeronautical planning.

---

## Credits and data licence

- Cartography: [Natural Earth](https://www.naturalearthdata.com/), 1:110m land data, **public domain**.
  Source file: [`ne_110m_land.geojson`](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_land.geojson) · [Terms of use](https://www.naturalearthdata.com/about/terms-of-use/)
- Privacy: there are no accounts and no data is sent anywhere. The CSV is only saved where you choose.
