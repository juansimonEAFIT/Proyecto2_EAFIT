# Estandarización Visual — LunchFlow Restaurante

# Contexto General

El perfil restaurante es el más interesante estratégicamente.

Porque a diferencia de:

- Admin → gestión operativa
- Empleado → autoservicio

El restaurante tiene un objetivo completamente distinto:

# velocidad.

---

# El restaurante NO usa el sistema para navegar

Lo usa para:

- escanear
- validar
- confirmar
- revisar registros rápidos

Y probablemente:

- desde celular
- de pie
- con presión operativa
- en horarios de alta demanda

---

# Conclusión importante

Este panel NO debe sentirse:

- administrativo
- empresarial
- denso
- complejo

Debe sentirse:

- rápido
- táctil
- limpio
- inmediato
- ultra simple

---

# Diagnóstico Actual

Actualmente el panel restaurante tiene:

## Cosas buenas

- simplicidad
- enfoque funcional
- navegación mínima
- pocos elementos distractores

---

# Problemas detectados

## 1. Muchísimo espacio vacío

Las pantallas parecen:

- wireframes
- prototipos tempranos
- interfaces sin terminar

---

## 2. Jerarquía débil

Actualmente:

- el escaneo no es protagonista
- los estados no destacan
- las acciones importantes no dominan visualmente

---

## 3. Mala optimización móvil

El sistema actualmente parece desktop-first.

Y eso es un problema.

Porque probablemente:

# el restaurante usará principalmente celular o tablet.

---

## 4. Contenedores gigantes

Mucho padding.

Demasiado espacio muerto.

Poca densidad útil.

---

# Objetivo Visual Correcto

El panel restaurante debería sentirse como:

- una app POS moderna
- una herramienta de validación rápida
- una interfaz de escaneo profesional

Inspiraciones:

- Shopify POS
- Uber Driver
- Mercado Pago Point
- apps de logística
- apps de check-in
- sistemas de acceso QR

---

# La gran decisión: ¿Dashboard o no?

# Respuesta corta:

NO necesitas un dashboard clásico.

Y de hecho:

# probablemente sería peor.

---

# ¿Por qué?

Porque el restaurante NO necesita:

- analytics complejos
- métricas grandes
- widgets
- KPIs administrativos

Necesita:

- entrar rápido
- escanear rápido
- validar rápido
- revisar consumos rápido

---

# La mejor solución

# Convertir “Escanear QR” en la home.

Es exactamente lo correcto.

---

# Nueva arquitectura recomendada

# Mobile-first total

```text
Inicio → Escanear QR
```

---

# Sidebar desktop

En desktop:

- mantener sidebar

---

# Mobile

En mobile:

- bottom navigation
- o navegación mínima flotante

---

# Nueva estructura ideal

```text
[Escanear]
[Consumos]
[Perfil]
```

Nada más.

---

# 1. ESCANEAR QR (HOME)

# Esta debe ser LA pantalla principal.

Y debe sentirse:

- inmediata
- rápida
- táctil
- moderna

---

# Problemas actuales

Actualmente:

- demasiado vacío
- demasiado centrado
- poca presencia visual
- la cámara no domina

---

# Nuevo enfoque

# Pantalla tipo app de escaneo

```text
┌────────────────────┐
│ Estado restaurante │
├────────────────────┤
│ Área escaneo QR    │
├────────────────────┤
│ Resultado scan     │
├────────────────────┤
│ Últimos registros  │
└────────────────────┘
```

---

# Muy importante

La cámara debe ocupar MUCHÍSIMO más espacio.

Actualmente parece:

- un botón cualquiera

---

# Nuevo enfoque

# Cámara protagonista

Usar:

```text
gran área visual
bordes suaves
feedback visual
scanner overlay
```

---

# Después del escaneo

Mostrar:

```text
✓ Ticket válido
Juan Simón
Almuerzo registrado
10:36 AM
```

Con:

- animación
- feedback inmediato
- color contextual

---

# Muy importante

La validación debe sentirse:

- instantánea
- confiable
- satisfactoria

---

# UX crítica

El restaurante NO debería:

- abrir modales
- confirmar demasiadas veces
- navegar entre pantallas

Todo debe pasar inline.

---

# Recomendación PRO

Agregar:

```text
Modo continuo de escaneo
```

Para validar múltiples empleados rápidamente.

---

# 2. CONSUMOS

Actualmente:

- correcta funcionalmente
- visualmente muy vacía

---

# Problema principal

La lista parece:

- tabla improvisada
- sin jerarquía
- demasiado separada

---

# Nuevo enfoque

# Lista tipo actividad

En vez de:

- tabla clásica

Usar:

```text
cards compactas
```

---

# Ejemplo

```text
[Avatar] Juan Simón
10:36 AM
Validado
```

Muchísimo mejor para móvil.

---

# Añadir

## Estados rápidos

- válido
- duplicado
- rechazado
- fuera de horario

---

# Toolbar superior

Actualmente correcta.

Pero:

- demasiado separada
- poco moderna

---

# Recomendación

Compactar:

```css
altura inputs
spacing
botón filtro
```

---

# Mobile

En móvil:

```text
fecha
↓
lista scrollable
```

No tabla.

---

# PERFIL RESTAURANTE

Actualmente no mostrado.

Pero debería ser extremadamente simple.

---

# Contenido ideal

```text
Restaurante
Estado conexión
Responsable
Última sincronización
Cerrar sesión
```

Nada más.

---

# Sistema Visual Recomendado

# El restaurante debe sentirse:

# más táctil que admin

# más rápido que empleado

---

# Diferencia conceptual

# Admin

Información.

# Empleado

Autoservicio.

# Restaurante

Acción inmediata.

---

# UI Density

El restaurante necesita:

- mayor densidad útil
- menos espacios muertos
- menos gigantismo

---

# Sistema de componentes

# restaurant-shell

# scanner-view

# scan-feedback-card

# consumption-feed

# restaurant-mobile-nav

---

# Sistema Mobile-First

# PRIORIDAD ABSOLUTA

Este perfil debe diseñarse:

# primero para celular.

No desktop.

---

# ¿Por qué?

Porque el flujo real será:

```text
Empleado llega
↓
Muestra QR
↓
Restaurante escanea
↓
Validación inmediata
↓
Siguiente persona
```

Todo en segundos.

---

# Recomendaciones mobile críticas

# 1. Botones enormes

Especialmente:

- iniciar cámara
- validar
- reintentar

---

# 2. Área QR grande

El scanner debe ocupar:

```css
width: 100%;
height: 50vh;
```

---

# 3. Navegación mínima

Idealmente:

```text
Escanear | Consumos | Perfil
```

---

# 4. Feedback inmediato

Usar:

- colores
- animaciones
- vibración (si existe soporte)
- sonido opcional

---

# 5. Modo oscuro opcional

MUY recomendado.

Porque restaurantes pueden:

- tener iluminación variable
- usar dispositivos baratos
- trabajar jornadas largas

---

# Recomendación MUY importante

# El sistema debería poder funcionar con una sola mano.

Eso cambia completamente el diseño.

---

# Implicaciones

# Acciones principales abajo

No arriba.

---

# Thumb zone optimization

En móvil:

- scanner abajo
- botones abajo
- navegación abajo

---

# Lo que NO debes hacer

# NO convertirlo en dashboard admin pequeño.

Sería un error gravísimo.

---

# NO agregar

- demasiadas métricas
- gráficos
- analytics complejos
- tablas enterprise
- widgets innecesarios

---

# La filosofía correcta

# Menos UI.

# Más velocidad.

---

# Dirección estética recomendada

El restaurante debería sentirse:

- más oscuro
- más táctil
- más operativo
- más rápido

Incluso podrías:

- usar menos fondo claro
- usar cards más contrastadas
- usar botones más sólidos

---

# Diferenciación visual ideal

# Admin

Formal.

# Empleado

Amigable.

# Restaurante

Operativo.

---

# Resultado esperado

Después del rediseño:

El restaurante debería sentir:

"Puedo validar 100 personas rápido sin pensar demasiado."

Y eso es EXACTAMENTE lo correcto.

---

# Conclusión Final

El perfil restaurante NO necesita más complejidad.

Necesita:

- velocidad
- eficiencia
- claridad
- diseño táctil
- mobile-first real

La mejor decisión estratégica es:

# usar “Escanear QR” como pantalla principal.

Y construir toda la experiencia alrededor de:

# validación rápida de consumo.

Eso haría que LunchFlow se sienta muchísimo más profesional y pensado para escenarios reales.

