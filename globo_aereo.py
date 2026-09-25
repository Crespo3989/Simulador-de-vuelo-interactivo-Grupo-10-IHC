"""Globo aéreo: geometría esférica 3D con Tkinter, Pillow y NumPy.
Ejecuta python globo_aereo.py. Continentes: Natural Earth, dominio público.
"""
import csv
import json
import math
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import ImageTk
from tierra_color import TierraColor

R = 6371.0
BG, PANEL, CYAN, GREEN, PINK = '#060e1c', '#102239', '#65dcff', '#6af1b0', '#ff759d'
# Centros urbanos aproximados, no aeropuertos. Latitud, longitud en grados.
CITIES = {
 'Quito, Ecuador':(-.18,-78.47), 'Guayaquil, Ecuador':(-2.17,-79.92),
 'Cuenca, Ecuador':(-2.90,-79.00), 'Bogotá, Colombia':(4.71,-74.07),
 'Medellín, Colombia':(6.24,-75.58), 'Lima, Perú':(-12.05,-77.04),
 'La Paz, Bolivia':(-16.50,-68.15), 'Santiago, Chile':(-33.45,-70.67),
 'Buenos Aires, Argentina':(-34.60,-58.38), 'Montevideo, Uruguay':(-34.90,-56.16),
 'Asunción, Paraguay':(-25.26,-57.58), 'São Paulo, Brasil':(-23.55,-46.63),
 'Río de Janeiro, Brasil':(-22.91,-43.17), 'Brasilia, Brasil':(-15.79,-47.88),
 'Caracas, Venezuela':(10.48,-66.90), 'Panamá, Panamá':(8.98,-79.52),
 'San José, Costa Rica':(9.93,-84.08), 'Ciudad de México, México':(19.43,-99.13),
 'Cancún, México':(21.16,-86.85), 'La Habana, Cuba':(23.11,-82.37),
 'Santo Domingo, R. Dominicana':(18.49,-69.93), 'Miami, USA':(25.76,-80.19),
 'Nueva York, USA':(40.71,-74.01), 'Washington, USA':(38.91,-77.04),
 'Chicago, USA':(41.88,-87.63), 'Los Ángeles, USA':(34.05,-118.24),
 'San Francisco, USA':(37.77,-122.42), 'Seattle, USA':(47.61,-122.33),
 'Toronto, Canadá':(43.65,-79.38), 'Vancouver, Canadá':(49.28,-123.12),
 'Montreal, Canadá':(45.50,-73.57), 'Madrid, España':(40.42,-3.70),
 'Barcelona, España':(41.39,2.17), 'Lisboa, Portugal':(38.72,-9.14),
 'París, Francia':(48.86,2.35), 'Londres, Reino Unido':(51.51,-.13),
 'Roma, Italia':(41.90,12.50), 'Berlín, Alemania':(52.52,13.41),
 'Ámsterdam, Países Bajos':(52.37,4.90), 'Zúrich, Suiza':(47.38,8.54),
 'Viena, Austria':(48.21,16.37), 'Atenas, Grecia':(37.98,23.73),
 'Estambul, Turquía':(41.01,28.98), 'Oslo, Noruega':(59.91,10.75),
 'Estocolmo, Suecia':(59.33,18.07), 'Helsinki, Finlandia':(60.17,24.94),
 'Reikiavik, Islandia':(64.15,-21.94), 'Moscú, Rusia':(55.76,37.62),
 'El Cairo, Egipto':(30.04,31.24), 'Casablanca, Marruecos':(33.57,-7.59),
 'Dakar, Senegal':(14.72,-17.47), 'Lagos, Nigeria':(6.52,3.38),
 'Nairobi, Kenia':(-1.29,36.82), 'Ciudad del Cabo, Sudáfrica':(-33.92,18.42),
 'Johannesburgo, Sudáfrica':(-26.20,28.05), 'Dubái, EAU':(25.20,55.27),
 'Doha, Catar':(25.29,51.53), 'Nueva Delhi, India':(28.61,77.21),
 'Mumbai, India':(19.08,72.88), 'Bangkok, Tailandia':(13.76,100.50),
 'Singapur, Singapur':(1.35,103.82), 'Yakarta, Indonesia':(-6.21,106.85),
 'Manila, Filipinas':(14.60,120.98), 'Pekín, China':(39.90,116.41),
 'Shanghái, China':(31.23,121.47), 'Hong Kong, China':(22.32,114.17),
 'Seúl, Corea del Sur':(37.57,126.98), 'Tokio, Japón':(35.68,139.69),
 'Osaka, Japón':(34.69,135.50), 'Sídney, Australia':(-33.87,151.21),
 'Melbourne, Australia':(-37.81,144.96), 'Perth, Australia':(-31.95,115.86),
 'Auckland, Nueva Zelanda':(-36.85,174.76), 'Honolulu, USA':(21.31,-157.86),
}

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def unit(v):
    n=math.sqrt(dot(v,v))
    return tuple(x/n for x in v)
def cross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def vector(lat,lon):
    p,l=math.radians(lat),math.radians(lon)
    return (math.cos(p)*math.cos(l), math.cos(p)*math.sin(l), math.sin(p))
def angle(a,b): return math.acos(max(-1,min(1,dot(a,b))))
def tangent(a,b):
    v=tuple(y-dot(a,b)*x for x,y in zip(a,b))
    if dot(v,v)<1e-14:
        v=cross(a,(0,0,1) if abs(a[2])<.9 else (0,1,0))
    return unit(v)
def travel(a,direction,radians):
    return unit(tuple(x*math.cos(radians)+y*math.sin(radians) for x,y in zip(a,direction)))
def arc(a,b,t): return travel(a,tangent(a,b),angle(a,b)*t)


class GloboAereo:
    def __init__(self,root):
        self.root=root
        root.title('AeroGlobo 3D · Laboratorio de navegación')
        root.geometry('1280x820'); root.minsize(1020,700); root.configure(bg=BG)
        self.points={name:vector(*ll) for name,ll in CITIES.items()}
        self.coasts=[]
        data=json.loads(Path(__file__).with_name('continentes.geojson').read_text(encoding='utf-8'))
        self.earth_renderer=TierraColor(data)
        self.earth_key=None
        for f in data['features']:
            g=f['geometry']; polygons=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
            for poly in polygons:
                self.coasts.append([vector(lat,lon) for lon,lat,*_ in poly[0]])
        self.grids=[]
        for lat in range(-60,90,30): self.grids.append([vector(lat,lon) for lon in range(-180,181,4)])
        for lon in range(-180,180,30): self.grids.append([vector(lat,lon) for lat in range(-90,91,4)])
        self.view_lat,self.view_lon=8.,-75.
        self.zoom=1.; self.keys=set(); self.drag=None
        self.active=False; self.paused=False; self.mode=None
        self.route=['Quito, Ecuador','Madrid, España']; self.leg=1
        self.pos=self.points[self.route[0]]; self.direction=tangent(self.pos,self.points[self.route[1]])
        self.elapsed=self.distance=0.; self.trace=[]; self.results={}; self.last=time.perf_counter()
        self.speed=950. # km por segundo de simulación acelerada
        self.build_ui(); self.refresh_route()
        root.bind('<KeyPress>',self.key_down); root.bind('<KeyRelease>',lambda e:self.keys.discard(e.keysym.lower()))
        root.bind('<FocusOut>',lambda e:self.keys.clear())
        self.tick()

    def label(self,parent,text,size=10,color='#edf5ff',**kw):
        return tk.Label(parent,text=text,bg=parent['bg'],fg=color,font=('Segoe UI',size),**kw)

    def build_ui(self):
        bar=tk.Frame(self.root,bg=BG); bar.pack(fill='x',padx=22,pady=15)
        self.label(bar,'A E R O G L O B O   /   3 D',21).pack(side='left')
        self.label(bar,f'{len(CITIES)} DESTINOS  ·  LATITUD / LONGITUD',10,CYAN).pack(side='right')
        body=tk.Frame(self.root,bg=BG); body.pack(fill='both',expand=True,padx=18,pady=(0,15))
        sidebar=tk.Frame(body,bg=PANEL,width=290); sidebar.pack(side='right',fill='y',padx=(14,0)); sidebar.pack_propagate(False)
        self.canvas=tk.Canvas(body,bg=BG,highlightthickness=0); self.canvas.pack(fill='both',expand=True)
        self.canvas.bind('<ButtonPress-1>',self.mouse_down)
        self.canvas.bind('<B1-Motion>',self.mouse_move)
        self.canvas.bind('<ButtonRelease-1>',lambda e:setattr(self,'drag',None))
        self.canvas.bind('<MouseWheel>',lambda e:self.zoom_by(1.1 if e.delta>0 else 1/1.1))
        self.canvas.bind('<Button-4>',lambda e:self.zoom_by(1.1)); self.canvas.bind('<Button-5>',lambda e:self.zoom_by(1/1.1))
        self.canvas.bind('<Configure>',lambda e:self.draw())
        self.label(sidebar,'PLAN DE VUELO',14,CYAN).pack(pady=(15,8))
        self.origin=tk.StringVar(value=self.route[0]); self.destination=tk.StringVar(value=self.route[-1])
        self.stops=[]; self.selectors=[]
        for title,var in [('Origen',self.origin),('Destino / siguiente escala',self.destination)]:
            self.label(sidebar,title,10,'#9bb3cb').pack(anchor='w',padx=12)
            cb=ttk.Combobox(sidebar,textvariable=var,values=sorted(CITIES),state='readonly',width=30)
            cb.pack(fill='x',padx=12,pady=(3,9)); cb.bind('<<ComboboxSelected>>',lambda e:self.refresh_route()); self.selectors.append(cb)
        actions=tk.Frame(sidebar,bg=PANEL); actions.pack(fill='x',padx=12)
        self.add_button=self.button(actions,'+ Escala',self.add_stop); self.add_button.pack(side='left',expand=True,fill='x')
        self.clear_button=self.button(actions,'Limpiar',self.clear_stops); self.clear_button.pack(side='left',expand=True,fill='x',padx=(6,0))
        self.route_text=self.label(sidebar,'',10,'#cfdeeb',justify='left',wraplength=265); self.route_text.pack(fill='x',padx=12,pady=10)
        for text,cmd in [('Volar automático',lambda:self.start('Automático')),('Volar manual',lambda:self.start('Manual')),
                         ('Pausar / continuar',self.pause),('Comparar resultados',self.compare),('Exportar resultados CSV',self.export)]:
            self.button(sidebar,text,cmd).pack(fill='x',padx=12,pady=3)
        self.follow=tk.BooleanVar(value=True)
        self.show_grid=tk.BooleanVar(value=False)
        tk.Checkbutton(sidebar,text='Mostrar meridianos y paralelos',variable=self.show_grid,
                       command=self.draw,bg=PANEL,fg=CYAN,selectcolor=BG,
                       activebackground=PANEL,activeforeground=CYAN).pack(pady=2)
        tk.Checkbutton(sidebar,text='Cámara sigue al avión',variable=self.follow,bg=PANEL,fg=CYAN,
                       selectcolor=BG,activebackground=PANEL,activeforeground=CYAN).pack(pady=6)
        self.metrics=self.label(sidebar,'',12,justify='left'); self.metrics.pack(fill='x',padx=15,pady=8)
        self.status=self.label(sidebar,'Selecciona una ruta.',10,GREEN,wraplength=260,justify='left'); self.status.pack(fill='x',padx=12,pady=4)
        self.label(sidebar,'Arrastrar: girar globo\nRueda: acercar / alejar\nWASD o flechas: norte/sur/este/oeste\nEspacio: pausar\n\nModelo acelerado: 950 km/s\nNo representa un vuelo real.',9,'#9bb3cb',justify='left').pack(side='bottom',anchor='w',padx=12,pady=14)

    def button(self,parent,text,cmd):
        return tk.Button(parent,text=text,command=cmd,bg='#1c3854',fg='white',activebackground='#315773',
                         activeforeground='white',relief='flat',padx=8,pady=7,cursor='hand2')

    def add_stop(self):
        if self.active:return
        name=self.destination.get()
        if name==self.origin.get() and not self.stops:return
        if not self.stops or self.stops[-1]!=name:
            if len(self.stops)>=5:messagebox.showinfo('Escalas','Máximo cinco escalas.'); return
            self.stops.append(name)
        self.refresh_route()

    def clear_stops(self):
        if not self.active:self.stops.clear(); self.refresh_route()

    def refresh_route(self):
        if self.active:return
        route=[self.origin.get()]+self.stops+[self.destination.get()]
        self.route=[route[0]]
        for name in route[1:]:
            if name!=self.route[-1]:self.route.append(name)
        self.pos=self.points[self.route[0]]; self.trace=[]; self.mode=None
        self.elapsed=self.distance=0; self.leg=1
        if len(self.route)>1:self.direction=tangent(self.pos,self.points[self.route[1]])
        self.reference=sum(angle(self.points[a],self.points[b])*R for a,b in zip(self.route,self.route[1:]))
        self.route_text.config(text=' → '.join(n.split(',')[0] for n in self.route)+f'\nRuta mínima: {self.reference:,.0f} km')
        self.view_lat,self.view_lon=CITIES[self.route[0]]; self.draw()

    def camera_basis(self):
        front=vector(self.view_lat,self.view_lon)
        east=unit(cross((0,0,1),front)); north=cross(front,east)
        return east,north,front

    def draw(self):
        if not hasattr(self,'canvas'):return
        c=self.canvas; c.delete('all')
        w,h=c.winfo_width(),c.winfo_height(); cx,cy=w/2,h/2
        radius=max(50,min(w,h)*.405*self.zoom)
        east,north,front=self.camera_basis()
        def project(v):return cx+radius*dot(v,east),cy-radius*dot(v,north),dot(v,front)
        # Fondo estelar estable: las estrellas no parpadean entre fotogramas.
        for i in range(90):
            sx=(i*137.508%997)/997*w; sy=(i*271.83%991)/991*h
            if (sx-cx)**2+(sy-cy)**2>(radius+22)**2:
                c.create_oval(sx,sy,sx+1.5,sy+1.5,fill='#46627b',outline='')
        for spread,color,stroke in [(15,'#0b1c30',12),(9,'#12314b',7),(4,'#245979',3)]:
            c.create_oval(cx-radius-spread,cy-radius-spread,cx+radius+spread,cy+radius+spread,
                          outline=color,width=stroke)
        key=(round(self.view_lat,4),round(self.view_lon,4),round(radius*2))
        if key!=self.earth_key:
            self.earth_photo=ImageTk.PhotoImage(self.earth_renderer.render(key[2],(east,north,front)))
            self.earth_key=key
        c.create_image(cx,cy,image=self.earth_photo)
        # Ocultación del hemisferio posterior. Intersecciones en el horizonte.
        def path(points,color,width=1):
            segment=[]
            previous=None
            for p in points:
                q=project(p)
                if previous is not None and (q[2]>=0)!=(previous[2]>=0):
                    t=previous[2]/(previous[2]-q[2])
                    edge=(previous[0]+t*(q[0]-previous[0]),previous[1]+t*(q[1]-previous[1]))
                    segment.extend(edge)
                    if len(segment)>=4:c.create_line(*segment,fill=color,width=width)
                    segment=list(edge) if q[2]>=0 else []
                if q[2]>=0:segment.extend(q[:2])
                previous=q
            if len(segment)>=4:c.create_line(*segment,fill=color,width=width)
        if self.show_grid.get():
            for grid in self.grids:path(grid,'#417a91')
        for a,b in zip(self.route,self.route[1:]):
            route_points=[arc(self.points[a],self.points[b],i/120) for i in range(121)]
            path(route_points,'#594d2e',5)
            path(route_points,'#ffdc87',2)
        if self.trace:path(self.trace,PINK if self.mode=='Manual' else CYAN,3)
        for name,p in self.points.items():
            x,y,z=project(p)
            if z<=.01:continue
            selected=name in self.route
            size=4 if selected else 2
            c.create_oval(x-size,y-size,x+size,y+size,fill='#ffd38a' if selected else '#b4dce7',outline='#15314b')
            if selected:
                label=c.create_text(x+11,y-12,text=name.split(',')[0],anchor='w',fill='#fff1ce',font=('Segoe UI',10,'bold'))
                box=c.bbox(label)
                plate=c.create_rectangle(box[0]-6,box[1]-4,box[2]+6,box[3]+4,fill='#102239',outline='#395367')
                c.tag_raise(label,plate)
        x,y,z=project(self.pos)
        if z>0:
            tip=project(travel(self.pos,self.direction,.015))
            theta=math.atan2(tip[1]-y,tip[0]-x)
            verts=[]
            for a,b in [(17,0),(2,-3),(-4,-13),(-8,-13),(-5,-2),(-13,-5),(-11,0),(-13,5),(-5,2),(-8,13),(-4,13),(2,3)]:
                verts.extend((x+a*math.cos(theta)-b*math.sin(theta),y+a*math.sin(theta)+b*math.cos(theta)))
            c.create_polygon(*verts,fill=PINK if self.mode=='Manual' else CYAN,outline='white')
        c.create_text(18,18,anchor='nw',fill=CYAN,text='TIERRA  /  PROYECCIÓN 3D',font=('Segoe UI',11,'bold'))
        c.create_text(18,h-25,anchor='w',fill='#92b3cc',text='Continentes: Natural Earth • Radio terrestre: 6 371 km • Automatización geométrica')
        remaining=angle(self.pos,self.points[self.route[min(self.leg,len(self.route)-1)]])*R
        self.metrics.config(text=f'{self.mode or "PREPARADO"}\nTiempo: {self.elapsed:.1f} s\nRecorrido: {self.distance:,.0f} km\nAl próximo destino: {remaining:,.0f} km')

    def start(self,mode):
        if len(self.route)<2:messagebox.showinfo('Ruta','Selecciona un destino distinto del origen.');return
        if self.active and not messagebox.askyesno('Nueva prueba','¿Descartar la prueba en curso?'):return
        self.mode=mode; self.active=True; self.paused=False; self.leg=1
        self.pos=self.points[self.route[0]]; self.direction=tangent(self.pos,self.points[self.route[1]])
        self.elapsed=self.distance=0.; self.trace=[self.pos]; self.keys.clear()
        self.results.pop((tuple(self.route),mode),None)
        for cb in self.selectors:cb.config(state='disabled')
        self.add_button.config(state='disabled'); self.clear_button.config(state='disabled')
        self.last=time.perf_counter(); self.canvas.focus_set()
        self.status.config(text='Vuelo iniciado. Visita cada destino en orden.')

    def pause(self):
        if self.active:
            self.paused=not self.paused; self.keys.clear()
            self.status.config(text='En pausa.' if self.paused else 'Vuelo en curso.')

    def key_down(self,event):
        key=event.keysym.lower()
        if key=='space' and key not in self.keys:self.pause()
        self.keys.add(key)

    def mouse_down(self,event):
        self.drag=(event.x,event.y); self.follow.set(False); self.canvas.focus_set()

    def mouse_move(self,event):
        if self.drag:
            self.view_lon-=(event.x-self.drag[0])*.35
            self.view_lat=max(-85,min(85,self.view_lat+(event.y-self.drag[1])*.35))
            self.drag=(event.x,event.y); self.draw()

    def zoom_by(self,factor):self.zoom=max(.65,min(1.45,self.zoom*factor));self.draw()

    def tick(self):
        now=time.perf_counter();dt=min(.08,now-self.last);self.last=now
        if self.active and not self.paused:
            self.elapsed+=dt; target=self.points[self.route[self.leg]]
            old=self.pos; step=self.speed*dt/R; moving=False
            if self.mode=='Automático':
                self.direction=tangent(old,target); moving=True
                self.pos=target if angle(old,target)<=step else travel(old,self.direction,step)
            else:
                dx=int(bool(self.keys&{'d','right'}))-int(bool(self.keys&{'a','left'}))
                dy=int(bool(self.keys&{'w','up'}))-int(bool(self.keys&{'s','down'}))
                if dx or dy:
                    east=cross((0,0,1),old)
                    if dot(east,east)<1e-12:east=(0,1,0)
                    east=unit(east);north=cross(old,east)
                    self.direction=unit(tuple(dx*a+dy*b for a,b in zip(east,north)))
                    self.pos=travel(old,self.direction,step);moving=True
            # Captura igual en ambos modos; incluye el segmento final en la distancia.
            moved=angle(old,self.pos)*R if moving else 0.
            arrival=angle(self.pos,target)*R<=65
            if arrival:
                moved+=angle(self.pos,target)*R;self.pos=target
            self.distance+=moved
            if moving or arrival:self.trace.append(self.pos)
            if arrival:
                self.leg+=1
                if self.leg==len(self.route):
                    self.active=False
                    self.results[(tuple(self.route),self.mode)]=(self.elapsed,self.distance)
                    for cb in self.selectors:cb.config(state='readonly')
                    self.add_button.config(state='normal');self.clear_button.config(state='normal')
                    self.status.config(text='Llegada completada. Ejecuta el otro modo para comparar.')
                else:self.status.config(text='Siguiente destino: '+self.route[self.leg])
            if self.follow.get():
                self.view_lat=max(-85,min(85,math.degrees(math.asin(self.pos[2]))))
                self.view_lon=math.degrees(math.atan2(self.pos[1],self.pos[0]))
            self.draw()
        self.root.after(33,self.tick)

    def compare(self):
        key=tuple(self.route)
        a=self.results.get((key,'Automático'));m=self.results.get((key,'Manual'))
        if not a or not m:messagebox.showinfo('Comparación','Completa ambos modos con exactamente la misma ruta.');return
        messagebox.showinfo('Comparación de la misma ruta',
            f'Automático: {a[0]:.1f} s | {a[1]:,.1f} km\nManual: {m[0]:.1f} s | {m[1]:,.1f} km\n\n'
            f'Manual − automático:\nTiempo: {m[0]-a[0]:+.1f} s\nDistancia: {m[1]-a[1]:+,.1f} km\n\n'
            'Valores positivos indican mayor consumo manual.\nTiempos acelerados, no duraciones reales de vuelos.')

    def export(self):
        if not self.results:messagebox.showinfo('Resultados','Completa primero una prueba.');return
        path=filedialog.asksaveasfilename(defaultextension='.csv',initialfile='resultados_globo.csv',filetypes=[('CSV','*.csv')])
        if not path:return
        try:
            with open(path,'w',newline='',encoding='utf-8-sig') as f:
                writer=csv.writer(f);writer.writerow(['ruta','modo','segundos_simulacion','km_esfera'])
                for (route,mode),(seconds,km) in self.results.items():writer.writerow([' → '.join(route),mode,round(seconds,3),round(km,3)])
        except OSError as exc:messagebox.showerror('No se pudo guardar',str(exc))
        else:self.status.config(text='Resultados exportados correctamente.')


if __name__=='__main__':
    root=tk.Tk()
    try:app=GloboAereo(root)
    except (OSError,ValueError) as exc:
        messagebox.showerror('Error de inicio',f'No se pudo cargar continentes.geojson:\n{exc}');root.destroy()
    else:root.mainloop()
