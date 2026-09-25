# AeroGlobo 3D · Laboratorio de navegación

*[Read in English](README.en.md)*

Simulador de rutas aéreas sobre un globo terrestre 3D interactivo, hecho con **Python**, **Tkinter**, **NumPy** y **Pillow**. Sirve para comparar un vuelo **automático** (que sigue el círculo máximo, la ruta más corta sobre la esfera) con uno **manual** controlado con el teclado, en la misma ruta.

> Es una herramienta educativa de geometría esférica, no un simulador de vuelo con física real. La velocidad está acelerada a propósito (950 km por segundo de simulación).

---

## Características

- **Globo 3D con proyección ortográfica**: se renderiza píxel a píxel a partir de coordenadas esféricas, con iluminación, halo atmosférico y oculta la cara posterior.
- **Cartografía real**: los continentes vienen de Natural Earth (1:110m, dominio público).
- **74 ciudades** de todos los continentes, con coordenadas aproximadas del centro urbano (no de los aeropuertos).
- **Rutas con escalas**: origen, hasta 5 escalas y destino.
- **Dos modos de vuelo**:
  - **Automático**: el avión sigue el arco de círculo máximo entre cada par de destinos.
  - **Manual**: tú pilotas con WASD o las flechas.
- **Métricas en vivo**: tiempo, distancia recorrida y distancia al próximo destino.
- **Comparación** entre ambos modos y **exportación a CSV**.
- Cuadrícula opcional de meridianos y paralelos, y cámara que sigue al avión.

---

## Requisitos

- Python 3.10 o superior
- Tkinter (viene con el instalador oficial de Python en Windows; en Linux instala `python3-tk`)
- NumPy ≥ 1.24
- Pillow ≥ 9.1

Solo se necesita Internet para instalar las dependencias la primera vez. El programa no usa claves API ni se conecta a Internet mientras corre.

---

## Instalación y ejecución

Desde la carpeta del proyecto:

```bash
python -m pip install -r requirements.txt
```

```bash
python globo_aereo.py
```

En Windows también puedes usar:

```bash
py globo_aereo.py
```

En Linux (Debian/Ubuntu), si falta Tkinter:

```bash
sudo apt install python3-tk
```

---

## Estructura del proyecto

```
aeroglobo_3d/
├── globo_aereo.py        # Aplicación principal: interfaz, cámara, rutas y lógica de vuelo
├── tierra_color.py       # Genera la textura del planeta y la renderiza sobre la esfera
├── continentes.geojson   # Contornos de los continentes (Natural Earth)
├── requirements.txt      # Dependencias de Python
├── README.md             # Documentación en español
├── README.en.md          # Documentación en inglés
└── LEEME_GLOBO.txt       # Notas originales del proyecto
```

`continentes.geojson` y `tierra_color.py` deben estar en la misma carpeta que `globo_aereo.py`. Si falta el GeoJSON, la aplicación muestra un error al iniciar.

---

## Cómo usarlo

### 1. Planificar la ruta
1. En **Origen**, elige la ciudad de salida.
2. Para añadir escalas, selecciona una ciudad en **Destino / siguiente escala** y pulsa **+ Escala**. Repite con cada escala (máximo 5).
3. Elige el destino final en **Destino / siguiente escala**.
4. **Limpiar** borra todas las escalas.

El panel muestra la ruta y su **distancia mínima** (la suma de los arcos de círculo máximo).

### 2. Volar
- **Volar automático**: el avión recorre la ruta óptima por su cuenta.
- **Volar manual**: pilotas tú. Tienes que pasar por cada destino en orden.

No puedes editar la ruta durante un vuelo. Si empiezas otro, el programa te pide confirmación antes de descartar el actual.

### 3. Comparar y exportar
- **Comparar resultados**: muestra la diferencia de tiempo y distancia entre el modo manual y el automático. Hay que completar los dos modos con exactamente la misma ruta.
- **Exportar resultados CSV**: guarda todos los resultados de la sesión.

---

## Controles

| Acción | Control |
|---|---|
| Girar el globo | Arrastrar con el ratón (desactiva el seguimiento de cámara) |
| Acercar / alejar | Rueda del ratón |
| Norte | `W` o `↑` |
| Sur | `S` o `↓` |
| Oeste | `A` o `←` |
| Este | `D` o `→` |
| Pausar / continuar | `Espacio` o el botón del panel |

Puedes combinar teclas para ir en diagonal; la velocidad se mantiene igual. Las direcciones son **geográficas** (norte, sur, este, oeste), no relativas a la pantalla, así que si giras la cámara no cambian.

---

## Modelo y medición

| Parámetro | Valor |
|---|---|
| Radio terrestre | 6 371 km (esfera perfecta) |
| Velocidad (ambos modos) | 950 km por segundo de simulación |
| Radio de llegada | 65 km del centro de la ciudad |
| Paso máximo por fotograma | 0,08 s |
| Frecuencia de actualización | ~30 fps |

- Las distancias se calculan como arcos sobre la esfera: `d = R · acos(a · b)`, donde `a` y `b` son vectores unitarios.
- El modo automático sigue círculos máximos entre destinos consecutivos.
- Al entrar en el radio de 65 km, se suma el tramo que falta hasta el centro de la ciudad. El criterio es el mismo en los dos modos.
- El tiempo solo cuenta mientras el vuelo está activo; las pausas no suman.
- No hay colisiones, viento, combustible ni obstáculos.

### Formato del CSV

Ejemplo con valores aproximados:

```csv
ruta,modo,segundos_simulacion,km_esfera
"Quito, Ecuador → Madrid, España",Automático,9.2,8737.99
```

El archivo se guarda en UTF-8 con BOM para que Excel muestre bien las tildes. Por cada ruta y modo se conserva solo el último resultado de la sesión; exporta antes de cerrar si quieres guardarlos.

---

## Detalles técnicos

- **Renderizado del globo** (`tierra_color.py`): al arrancar, rasteriza los polígonos del GeoJSON en una textura equirectangular de 2048×1024 con colores estilizados (océano, costas, tierra y hielo polar). En cada fotograma, lanza un rayo inverso por píxel contra la esfera, calcula su latitud y longitud, y toma el color de la textura. La resolución interna tiene un tope de 560 px para que vaya fluido en equipos modestos.
- **Líneas sobre el globo** (rutas, estela y cuadrícula): se proyectan en 3D y se recortan exactamente en el horizonte, así no aparecen segmentos del hemisferio oculto.
- **Geometría esférica** (`globo_aereo.py`): vectores unitarios, vector tangente hacia el destino, desplazamiento a lo largo de un círculo máximo e interpolación de arcos. También maneja los casos especiales de puntos antipodales y los polos.

---

## Limitaciones

- Los colores del planeta son decorativos: no representan clima, relieve ni profundidad del océano.
- La iluminación está fija respecto a la cámara; no simula el día y la noche.
- Las ciudades son centros urbanos aproximados, no aeropuertos.
- Los tiempos están acelerados y no sirven para estimar la duración real de un vuelo.
- La automatización es geométrica y determinista; no es inteligencia artificial.
- No sustituye la planificación aeronáutica real.

---

## Créditos y licencia de datos

- Cartografía: [Natural Earth](https://www.naturalearthdata.com/), datos terrestres 1:110m, **dominio público**.
  Archivo original: [`ne_110m_land.geojson`](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_land.geojson) · [Términos de uso](https://www.naturalearthdata.com/about/terms-of-use/)
- Privacidad: no hay cuentas ni se envían datos. El CSV solo se guarda donde tú indiques.
