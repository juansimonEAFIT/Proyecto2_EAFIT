# Sprint 1 - Issues #6 y #7: Funcionalidad QR Completa

Sistema de códigos QR para identificación de empleados y registro de consumo de almuerzos en LunchFlow.

## Estado Actual del Código

Después de explorar el proyecto, **gran parte de la funcionalidad ya está implementada**:

| Componente | Estado | Detalles |
|---|---|---|
| `Empleado.codigo_qr` (UUID) | ✅ Hecho | Auto-generado con `uuid.uuid4` en el modelo |
| Señal [crear_perfil](file:///c:/Users/sebas/OneDrive/Escritorio/p2/users/signals.py#6-17) | ✅ Hecho | Crea [Empleado](file:///c:/Users/sebas/OneDrive/Escritorio/p2/users/models.py#30-52) al crear un [User](file:///c:/Users/sebas/OneDrive/Escritorio/p2/users/models.py#9-26) con rol empleado |
| Vista [ver_qr_empleado](file:///c:/Users/sebas/OneDrive/Escritorio/p2/schedule/views.py#134-159) | ✅ Hecho | Genera URL con el UUID y la pasa al template |
| Template [qr_empleado.html](file:///c:/Users/sebas/OneDrive/Escritorio/p2/schedule/templates/schedule/qr_empleado.html) | ✅ Hecho | Muestra QR usando API externa `api.qrserver.com` |
| Vista [consumir_almuerzo_qr](file:///c:/Users/sebas/OneDrive/Escritorio/p2/schedule/views.py#198-283) | ✅ Hecho | Valida empleado, estado activo, tiquetes y registra consumo |
| Template [consumo_qr_resultado.html](file:///c:/Users/sebas/OneDrive/Escritorio/p2/schedule/templates/schedule/consumo_qr_resultado.html) | ✅ Hecho | Muestra resultado (aprobado/denegado) con detalles |
| Dashboard del restaurante | ⚠️ Placeholder | Dice "Panel en construcción", **no tiene escáner QR** |
| Sidebar del restaurante | ⚠️ Mínimo | Solo tiene link a Inicio y Cerrar sesión |

### Criterios de aceptación Issue #6
- ✅ Cada empleado tiene un QR único → `codigo_qr = UUIDField(default=uuid.uuid4)`
- ✅ El QR se puede visualizar → Vista [ver_qr_empleado](file:///c:/Users/sebas/OneDrive/Escritorio/p2/schedule/views.py#134-159) + template [qr_empleado.html](file:///c:/Users/sebas/OneDrive/Escritorio/p2/schedule/templates/schedule/qr_empleado.html)
- ✅ El QR está asociado correctamente al usuario → Foreign key `Empleado → User`

### Criterios de aceptación Issue #7
- ⚠️ El QR puede ser leído correctamente → La URL funciona pero **no hay escáner en el dashboard del restaurante**
- ✅ El sistema identifica al empleado → [consumir_almuerzo_qr](file:///c:/Users/sebas/OneDrive/Escritorio/p2/schedule/views.py#198-283) busca por UUID
- ⚠️ Se muestra confirmación de lectura → Solo funciona si acceden directamente a la URL del QR

## Proposed Changes

### Lo que falta: Escáner QR real en el Dashboard del Restaurante

El **único gap significativo** es que el dashboard del restaurante ([dashboard_restaurante.html](file:///c:/Users/sebas/OneDrive/Escritorio/p2/core/templates/core/dashboard_restaurante.html)) es un placeholder que dice "Panel en construcción". Necesita un escáner QR funcional con cámara.

---

### Componente: Dashboard del Restaurante

#### [MODIFY] [dashboard_restaurante.html](file:///c:/Users/sebas/OneDrive/Escritorio/p2/core/templates/core/dashboard_restaurante.html)

Reemplazar el placeholder con un escáner QR funcional:
- Integrar librería **html5-qrcode** (CDN, sin instalación) para acceso a la cámara del dispositivo
- Al escanear un QR, extraer la URL con el UUID y redirigir automáticamente a la vista [consumir_almuerzo_qr](file:///c:/Users/sebas/OneDrive/Escritorio/p2/schedule/views.py#198-283)
- Mostrar interfaz clara con botón para iniciar/detener la cámara
- Diseño responsivo y consistente con el estilo existente del proyecto

#### [MODIFY] [sidebar_restaurante.html](file:///c:/Users/sebas/OneDrive/Escritorio/p2/core/templates/core/includes/sidebar_restaurante.html)

Agregar enlace al escáner QR en el sidebar para fácil acceso.

#### [MODIFY] [core/views.py](file:///c:/Users/sebas/OneDrive/Escritorio/p2/core/views.py)

Pasar información contextual adicional a la vista del restaurante (últimos consumos registrados hoy, estadísticas básicas).

> [!NOTE]
> No es necesario modificar modelos, migraciones, ni dependencias del [requirements.txt](file:///c:/Users/sebas/OneDrive/Escritorio/p2/requirements.txt) ya que usaremos la librería QR desde CDN y la lógica backend ya está completamente implementada.

## Verification Plan

### Verificación Manual (recomendada)

Ya que el proyecto usa PostgreSQL con Docker, y la verificación principal es visual/interactiva:

1. **Issue #6 - QR del empleado:**
   - Iniciar sesión como empleado
   - Ir a "Ver mi QR" desde el dashboard
   - Verificar que se muestra un código QR visible y escaneable
   - Verificar que cada empleado tiene un QR diferente

2. **Issue #7 - Escaneo desde restaurante:**
   - Iniciar sesión como usuario con rol "restaurante"
   - En el dashboard, verificar que aparece el escáner QR
   - Escanear un QR de empleado con la cámara del dispositivo
   - Verificar que se muestra la confirmación de lectura (aprobado/denegado)
   - Verificar que el consumo queda registrado en la base de datos

> [!IMPORTANT]
> Para la verificación necesitamos que el sistema esté corriendo (Docker o local). ¿Tienes el entorno Docker configurado o prefieres correr el proyecto localmente?
