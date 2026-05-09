# Estandarización Visual Completa — LunchFlow Admin

# Contexto General

Después del rediseño del dashboard principal, el sistema ganó:

- jerarquía visual
- identidad moderna
- sensación SaaS
- mejor UX operativa

Sin embargo, el resto de las pantallas aún conservan patrones visuales antiguos.

Actualmente el sistema mezcla:

- layouts modernos
- formularios clásicos
- tablas antiguas
- spacing inconsistente
- headers diferentes
- estilos de cards incompatibles

Esto rompe:

- continuidad visual
- percepción profesional
- sensación de producto unificado

---

# Objetivo General

Crear un sistema visual coherente para TODO el panel administrativo.

El objetivo NO es solo “hacerlo bonito”.

El objetivo es:

- que todas las páginas parezcan parte del mismo producto
- que exista un sistema visual consistente
- que el usuario reconozca patrones
- reducir carga cognitiva
- elevar percepción enterprise

---

# Problemas Detectados

# 1. Headers inconsistentes

Cada página tiene:

- tamaños distintos
- alineaciones distintas
- spacing distinto
- algunos centrados
- otros alineados a la izquierda

## Ejemplo

### Reportes
Muy moderno.

### Registrar Personal
Demasiado clásico.

### Configuración Inventario
Muy vacío.

### Analíticas
Visualmente desbalanceado.

---

# 2. Cards incompatibles

Actualmente existen:

- cards minimalistas
- cards con borde rojo
- cards con fondo azul
- cards muy anchas
- cards tipo formulario viejo

No existe un sistema único.

---

# 3. Espaciado inconsistente

Hay páginas donde:

- sobra espacio
- otras están comprimidas
- otras tienen padding excesivo

Esto afecta muchísimo la percepción de calidad.

---

# 4. Formularios antiguos

Muchos formularios siguen teniendo:

- estructura vertical clásica
- demasiado texto
- inputs gigantes
- botones desbalanceados

No siguen el lenguaje moderno del dashboard nuevo.

---

# 5. Tablas antiguas

Las tablas funcionan.

Pero visualmente:

- parecen CRUD tradicional
- no parecen SaaS moderno
- tienen demasiadas líneas
- demasiado espacio muerto

---

# Dirección Visual Global

# El sistema debería sentirse como:

- Stripe Dashboard
- Linear
- Clerk
- Vercel
- Notion Admin
- Retool moderno

NO como:

- ERP antiguo
- panel Bootstrap
- CRUD universitario

---

# Nuevo Sistema Base

# 1. Layout Universal

TODAS las páginas deben usar:

```text
┌────────────────────────────┐
│ Header contextual          │
├────────────────────────────┤
│ Toolbar / filtros          │
├────────────────────────────┤
│ Contenido principal        │
└────────────────────────────┘
```

---

# 2. Header estándar

TODAS las páginas deben tener:

## Estructura

```text
Título
Descripción corta contextual
```

## Ejemplo

### Registrar Pago

```text
Registrar pago
Gestiona pagos manuales y actualiza balances.
```

### Analíticas

```text
Analíticas
Visualiza métricas y tendencias operativas.
```

---

# 3. Eliminar títulos gigantes rojos

Actualmente varias páginas usan:

- headers rojos enormes
- centrados
- demasiado dominantes

Eso rompe la jerarquía moderna.

## Nuevo enfoque

Usar:

```css
font-size: 36px;
font-weight: 700;
color: var(--color-oscuro);
```

Y reservar el rojo solo para:

- estados importantes
- botones primarios
- métricas críticas

---

# 4. Nuevo sistema de contenedores

Actualmente algunos formularios parecen “cajas flotantes”.

## Nuevo enfoque

Usar máximo:

```css
max-width: 1200px;
```

Y dividir contenido usando:

- grids
- secciones
- columnas

NO usando:

- una sola card gigante centrada

---

# Estandarización por Página

---

# 1. SOLICITUDES

## Estado actual

Es la más cercana al nuevo sistema.

Pero:

- filtros demasiado pegados
- tabla muy plana
- falta jerarquía visual

---

## Rediseño

# Nuevo Header

```text
Solicitudes
Gestiona solicitudes y revisa estados de aprobación.
```

---

# Toolbar superior

Mover filtros a:

```text
┌─────────────────────────┐
│ búsqueda global         │
│ filtros secundarios     │
└─────────────────────────┘
```

Con:

- búsqueda
- mes
- año
- empleado
- estado

---

# Tabla nueva

## Mejoras

- más compacta
- hover states
- avatar usuario
- badges más pequeños
- líneas más suaves

---

# 2. REGISTRAR PAGO

## Problema actual

Parece:

- formulario aislado
- demasiado vacío
- desbalanceado

---

## Nuevo enfoque

# Layout dividido

```text
┌───────────────────────┬────────────────┐
│ Formulario            │ Resumen        │
│                       │ empleado       │
└───────────────────────┴────────────────┘
```

---

# Panel lateral

Mostrar:

- saldo pendiente
- últimos pagos
- estado
- consumos recientes

Esto hace la experiencia MUCHO más contextual.

---

# Inputs

Reducir altura.

Menos sensación de “formulario gubernamental”.

---

# Botones

Actualmente:

- demasiado anchos
- demasiado pesados

## Nuevo

Botones compactos:

```css
height: 48px;
padding: 0 20px;
```

---

# 3. INVENTARIO

## Problema actual

La primera pantalla:

- está vacía
- no aporta valor
- solo redirecciona

---

# Solución

Eliminar esa pantalla intermedia.

Entrar directamente a:

```text
Configuración de Tickets
```

---

# CONFIGURACIÓN DE TICKETS

Esta página tiene potencial.

Pero:

- demasiados bloques verticales
- falta separación visual
- inputs mal distribuidos

---

# Nuevo Layout

```text
┌────────────────────────────┐
│ Estado actual              │
├────────────┬───────────────┤
│ Stock      │ Precio        │
└────────────┴───────────────┘

┌────────────────────────────┐
│ Ajustes mensuales          │
└────────────────────────────┘

┌────────────────────────────┐
│ Historial de cambios       │
└────────────────────────────┘
```

---

# Recomendación importante

Agregar:

- historial de cambios
- quién modificó stock
- cuándo
- motivo

Esto eleva muchísimo percepción enterprise.

---

# 4. REPORTES

Esta es actualmente la página MÁS moderna.

Tiene:

- hero section
- buena composición
- profundidad visual

---

# Qué mejorar

## El formulario debajo aún parece antiguo.

---

# Solución

Usar:

- grid de filtros
- menos altura
- spacing más compacto
- mejor alineación

---

# Además

Separar:

- filtros
- exportaciones

Actualmente están mezclados.

---

# Recomendación PRO

Agregar:

```text
Exportaciones recientes
```

Con:

- fecha
- tipo
- usuario
- botón descargar

Muy estilo Stripe.

---

# 5. ANALÍTICAS

## Problema actual

Es MUY técnica visualmente.

Demasiados:

- inputs
- checkboxes
- botones
- controles juntos

Parece panel de ingeniería.

---

# Nuevo enfoque

Separar:

# A. Configuración

Filtros y parámetros.

# B. Visualización

Gráfico grande protagonista.

---

# Nueva estructura

```text
┌────────────────────────────┐
│ Header                     │
├────────────────────────────┤
│ Configuración filtros      │
├────────────────────────────┤
│ Gráfico principal          │
├────────────────────────────┤
│ Métricas derivadas         │
└────────────────────────────┘
```

---

# Checkbox redesign

Actualmente se ven antiguos.

Usar:

- switches
- pills
- segmented controls

Mucho más moderno.

---

# 6. GESTIÓN PERSONAL

Muy buena base.

Pero:

- demasiado plana
- parece tabla default

---

# Mejoras

# Avatar usuario

Agregar:

- iniciales
- foto opcional

---

# Quick actions

Mover:

- editar
- ver consumos

A menú contextual.

---

# Añadir KPIs arriba

```text
Usuarios activos
Restaurantes
Pagos pendientes
```

Esto ayuda muchísimo.

---

# 7. HISTORIAL CONSUMOS

## Problema actual

Muy vacío.

Mucho espacio muerto.

---

# Nuevo enfoque

Convertirlo en:

```text
Perfil + actividad
```

---

# Layout recomendado

```text
┌────────────┬───────────────────┐
│ Perfil     │ Historial         │
│ empleado   │ consumos          │
└────────────┴───────────────────┘
```

---

# Panel lateral

Mostrar:

- nombre
- área
- saldo
- consumos totales
- último consumo

---

# 8. EDITAR CONSUMO

Actualmente:

- demasiado centrado
- mucho espacio vacío
- parece modal gigante

---

# Nuevo enfoque

Usar:

```text
┌────────────────────────────┐
│ Información original       │
├────────────────────────────┤
│ Corrección                 │
├────────────────────────────┤
│ Historial auditoría        │
└────────────────────────────┘
```

---

# Muy importante

Mostrar:

- valor anterior
- nuevo valor
- quién editó
- cuándo

Esto aumenta muchísimo la confianza.

---

# 9. REGISTRAR PERSONAL

## Problema actual

Demasiado largo.

Demasiado vertical.

---

# Nuevo enfoque

# Wizard por pasos

```text
Paso 1 → Acceso
Paso 2 → Información personal
Paso 3 → Configuración
```

---

# Beneficios

- menos intimidante
- más moderno
- mejor UX
- menor carga cognitiva

---

# Sistema Global de UI

# 1. Sistema de spacing

Usar SIEMPRE:

```css
8px
16px
24px
32px
48px
```

---

# 2. Sistema de radios

```css
Cards: 24px
Inputs: 14px
Botones: 14px
Badges: 999px
```

---

# 3. Sistema de sombras

Reducir sombras fuertes.

Usar:

```css
box-shadow: 0 8px 24px rgba(15,23,42,0.05);
```

---

# 4. Sistema de botones

# Primario

Rojo LunchFlow.

# Secundario

Outline suave.

# Ghost

Solo texto.

---

# 5. Inputs

Todos deben:

- tener misma altura
- mismo radio
- mismo focus state
- mismo spacing

---

# 6. Tablas

Todas deben compartir:

- padding
- tipografía
- hover
- badges
- headers

---

# Recomendación Arquitectónica

# Crear componentes reutilizables

## Ejemplos

### page-header

### section-card

### stats-row

### data-table

### form-grid

### action-toolbar

### empty-state

---

# Resultado Esperado

Con esta estandarización:

LunchFlow dejará de sentirse como:

- varias páginas separadas

Y empezará a sentirse como:

- un verdadero producto SaaS profesional.

---

# Prioridad de Rediseño

# Prioridad Alta

1. Registrar Pago
2. Analíticas
3. Registrar Personal
4. Inventario

---

# Prioridad Media

5. Solicitudes
6. Gestión Personal
7. Historial Consumos

---

# Prioridad Baja

8. Editar Consumo
9. Ajustes secundarios

---

# Conclusión

El dashboard nuevo ya definió una identidad visual fuerte.

Ahora el siguiente paso NO es crear estilos nuevos.

Es:

- consolidar patrones
- reutilizar componentes
- estandarizar layouts
- reducir inconsistencias
- mejorar jerarquía visual

Ese es exactamente el paso que transforma un proyecto universitario en un producto que parece real.

