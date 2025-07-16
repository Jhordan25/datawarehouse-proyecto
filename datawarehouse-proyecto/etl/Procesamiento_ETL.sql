USE DataWar;
GO

-- Cargar datos en dimensiones de Hechos_Pago (normalización: coalescing valores nulos, casting tipos)
INSERT INTO Dim_Cliente_Pago (
    IdCliente, Nombre, Apellidos, Correo, Telefono, Nacionalidad, TipoCliente, FechaRegistro, Actividad_Economica
)
SELECT DISTINCT
    IdCliente, 
    COALESCE(Nombres, 'Desconocido') AS Nombre, 
    COALESCE(Apellidos, 'Desconocido') AS Apellidos, 
    Correo, 
    CAST(Telefono AS VARCHAR(20)) AS Telefono, 
    Nacionalidad, 
    tipo AS TipoCliente, 
    FechaRegistro, 
    COALESCE(Actividad_Economica, 'No especificada') AS Actividad_Economica
FROM Hechos_Pago.dbo.Cliente;
GO

INSERT INTO Dim_Forma_Pago_Pago (
    IdFormaPago, TipoFormaPago, EntidadBancaria, TipoTarjeta
)
SELECT DISTINCT
    IdFormaPago, 
    TipoFormaPago, 
    COALESCE(EntidadBancaria, 'No especificado') AS EntidadBancaria, 
    COALESCE(TipoTarjeta, 'No especificado') AS TipoTarjeta
FROM Hechos_Pago.dbo.Forma_de_Pago;
GO

INSERT INTO Dim_Habitacion_Pago (
    IdHabitacion, Numero_Habitacion, TipoHabitacion, Capacidad, PrecioBase
)
SELECT DISTINCT
    IdHabitacion, 
    Numero_Habitacion, 
    TipoHabitacion, 
    Capacidad, 
    PrecioBase
FROM Hechos_Pago.dbo.Habitacion;
GO

INSERT INTO Dim_Reserva_Pago (
    IdReserva, FechaReserva, FechaCheckin, FechaCheckout, EstadoReserva, NumeroNoches, OrigenReserva
)
SELECT DISTINCT
    IdReserva, 
    FechaReserva, 
    CASE WHEN NumeroNoches < 0 THEN FechaCheckout ELSE FechaCheckin END AS FechaCheckin,
    CASE WHEN NumeroNoches < 0 THEN FechaCheckin ELSE FechaCheckout END AS FechaCheckout,
    EstadoReserva, 
    CASE WHEN NumeroNoches < 0 THEN DATEDIFF(DAY, FechaCheckout, FechaCheckin) ELSE NumeroNoches END AS NumeroNoches,
    OrigenReserva
FROM Hechos_Pago.dbo.Reserva;
GO

INSERT INTO Dim_Empleado_Pago (
    IdEmpleado, Nombres, Apellidos, Puesto, Departamento
)
SELECT DISTINCT
    IdEmpleado, 
    COALESCE(Nombres, 'Desconocido') AS Nombres, 
    COALESCE(Apellidos, 'Desconocido') AS Apellidos, 
    Puesto, 
    COALESCE(Departamento, 'Sin departamento') AS Departamento
FROM Hechos_Pago.dbo.Empleado;
GO

-- Cargar datos en dimensiones de Hecho_Satisfaccion
INSERT INTO Dim_CanalAtencion_Satisfaccion (
    CanalAtencionID, NombreCanal, Descripcion, HorarioAtencion, Responsable
)
SELECT DISTINCT
    CanalAtencionID, 
    NombreCanal, 
    Descripcion, 
    CASE 
        WHEN HorarioAtencion = '24/7' THEN '00:00 - 23:59' 
        ELSE HorarioAtencion 
    END AS HorarioAtencion,
    Responsable
FROM Hecho_Satisfaccion.dbo.Dim_CanalAtencion;
GO

INSERT INTO Dim_MotivoInsatisfaccion_Satisfaccion (
    MotivoInsatisfaccionID, Categoria, DescripcionMotivo, NivelGravedad
)
SELECT DISTINCT
    MotivoInsatisfaccionID, 
    Categoria, 
    DescripcionMotivo, 
    NivelGravedad
FROM Hecho_Satisfaccion.dbo.Dim_MotivoInsatisfaccion;
GO

INSERT INTO Dim_TipoCliente_Satisfaccion (
    TipoClienteID, NombreTipoCliente
)
SELECT DISTINCT
    TipoClienteID, 
    NombreTipoCliente
FROM Hecho_Satisfaccion.dbo.Dim_TipoCliente;
GO

INSERT INTO Dim_TipoHabitacion_Satisfaccion (
    ID_Tipo_Habitacion, Nombre_Tipo_Habitacion, Descripcion, Estado
)
SELECT DISTINCT
    ID_Tipo_Habitacion, 
    Nombre_Tipo_Habitacion, 
    CAST(Descripcion AS VARCHAR(MAX)) AS Descripcion, 
    Estado
FROM Hecho_Satisfaccion.dbo.Dim_TipoHabitacion;
GO

INSERT INTO Dim_TipoQueja_Satisfaccion (
    TipoQuejaID, NombreTipoQueja, Descripcion
)
SELECT DISTINCT
    TipoQuejaID, 
    NombreTipoQueja, 
    Descripcion
FROM Hecho_Satisfaccion.dbo.Dim_TipoQueja;
GO

INSERT INTO Dim_TipoServicio_Satisfaccion (
    TipoServicioID, NombreServicio, Descripcion, Estado
)
SELECT DISTINCT
    TipoServicioID, 
    NombreServicio, 
    Descripcion, 
    Estado
FROM Hecho_Satisfaccion.dbo.Dim_TipoServicio;
GO

-- Cargar datos en dimensiones de Hechos_Ventas
INSERT INTO Dim_Cliente_Ventas (
    IdCliente, Nombre, Apellidos, Correo, Telefono, Nacionalidad, TipoCliente, FechaRegistro
)
SELECT DISTINCT
    IdCliente, 
    Cliente_Nombres AS Nombre, 
    Cliente_Apellidos AS Apellidos, 
    Cliente_Correo AS Correo, 
    CAST(Cliente_Telefono AS VARCHAR(20)) AS Telefono, 
    Nacionalidad, 
    tipo AS TipoCliente, 
    FechaRegistro
FROM HECHO_VENTAS.dbo.Dim_Cliente_Segmento;
GO

INSERT INTO Dim_Forma_Pago_Ventas (
    IdFormaPago, TipoFormaPago, EntidadBancaria
)
SELECT DISTINCT
    ID_Metodo_Pago AS IdFormaPago, 
    Tipo_Forma_Pago AS TipoFormaPago, 
    COALESCE(Entidad_Bancaria, 'No especificado') AS EntidadBancaria
FROM HECHO_VENTAS.dbo.Dim_Metodo_Pago;
GO

INSERT INTO Dim_Periodo_Ventas (
    ID_Temporada, Nombre_Temporada, Fecha_Inicio_Temporada, Fecha_Fin_Temporada, Factor_Precio_Temporada
)
SELECT DISTINCT
    ID_Temporada, 
    Nombre_Temporada, 
    Fecha_Inicio_Temporada, 
    Fecha_Fin_Temporada, 
    Factor_Precio_Temporada
FROM HECHO_VENTAS.dbo.Dim_Periodo;
GO

INSERT INTO Dim_Estimacion_Ventas (
    ID_Estimacion, Fecha_Cotizacion, ID_Cliente, Numero_Adultos, Numero_Ninos, ID_Tipo_Habitacion, Cantidad_Habitaciones, Servicios_Adicionales, Precio_Total, Estado, ID_Medio_Contacto
)
SELECT DISTINCT
    ID_Estimacion, 
    Fecha_Cotizacion, 
    ID_Cliente, 
    Numero_Adultos, 
    Numero_Ninos, 
    ID_Tipo_Habitacion, 
    Cantidad_Habitaciones, 
    CAST(Servicios_Adicionales AS VARCHAR(MAX)) AS Servicios_Adicionales, 
    Precio_Total, 
    Estado, 
    ID_Medio_Contacto
FROM HECHO_VENTAS.dbo.Dim_Estimacion;
GO

INSERT INTO Dim_Comprobante_Ventas (
    ID_Comprobante, ID_Reserva, Fecha_Comprobante, Numero_Comprobante, ID_Cliente, Subtotal, Impuestos, Total, ID_Forma_Pago, ID_Medio_Pago
)
SELECT DISTINCT
    ID_Comprobante, 
    ID_Reserva, 
    Fecha_Comprobante, 
    Numero_Comprobante, 
    ID_Cliente, 
    Subtotal, 
    Impuestos, 
    Total, 
    ID_Forma_Pago, 
    ID_Medio_Pago
FROM HECHO_VENTAS.dbo.Dim_Comprobante;
GO

INSERT INTO Dim_Campana_Promocion_Ventas (
    ID_Campana_Promocion, Nombre_Campana_Promocion, ID_Temporada, Fecha_Inicio, Fecha_Fin, Objetivo_Campana_Promocion, Justificacion_Campana, Nombre_Canal_Promocion, Descripcion_Canal_Promocion
)
SELECT DISTINCT
    ID_Campana_Promocion, 
    Nombre_Campana_Promocion, 
    ID_Temporada, 
    Fecha_Inicio, 
    Fecha_Fin, 
    Objetivo_Campana_Promocion, 
    Justificacion_Campana, 
    Nombre_Canal_Promocion, 
    Descripcion_Canal_Promocion
FROM HECHO_VENTAS.dbo.Dim_Campana_Promocion;
GO

-- Cargar datos en las tablas de hechos (cada uno usa sus dimensiones independientes)
-- Se agrega SELECT DISTINCT para filtrar y evitar inserción de datos repetidos exactos
INSERT INTO Fact_Pagos (
    Fecha, IdCliente, IdHabitacion, IdReserva, IdFormaPago, IdEmpleado, monto_pago, descuento, impuestos, total_factura
)
SELECT DISTINCT
    fecha_pago AS Fecha,
    cliente_id AS IdCliente,
    habitacion_id AS IdHabitacion,
    reserva_id AS IdReserva,
    forma_pago_id AS IdFormaPago,
    empleado_id AS IdEmpleado,
    monto_pago,
    descuento,
    impuestos,
    total_factura
FROM Hechos_Pago.dbo.Hechos_Pago;
GO

INSERT INTO Fact_Satisfaccion (
    Fecha, TipoClienteID, ID_Tipo_Habitacion, TipoServicioID, TipoQuejaID, CanalAtencionID, MotivoInsatisfaccionID, NivelSatisfaccion, Resuelto
)
SELECT DISTINCT
    FechaAtencion AS Fecha,
    TipoClienteID,
    TipoHabitacionID AS ID_Tipo_Habitacion,
    TipoServicioID,
    TipoQuejaID,
    CanalAtencionID,
    MotivoInsatisfaccionID,
    NivelSatisfaccion,
    Resuelto
FROM Hecho_Satisfaccion.dbo.Hecho_Satisfaccion;
GO

INSERT INTO Fact_Ventas (
    Fecha, ID_Comprobante, ID_Estimacion, IdCliente, IdFormaPago, ID_Temporada, ID_Campana_Promocion, Subtotal, Impuestos, Total, Precio_Total_Cotizacion
)
SELECT DISTINCT
    Fecha_Venta AS Fecha,
    ID_Comprobante,
    ID_Estimacion,
    ID_Cliente AS IdCliente,
    ID_Metodo_Pago AS IdFormaPago,
    ID_Temporada,
    ID_Campana_Promocion,
    Subtotal,
    Impuestos,
    Total,
    Precio_Total_Cotizacion
FROM HECHO_VENTAS.dbo.Hechos_Ventas;
GO

-- Crear índices para mejorar el rendimiento (normalización incluye optimización)
CREATE INDEX IX_Fact_Pagos_Fecha ON Fact_Pagos (Fecha);
CREATE INDEX IX_Fact_Pagos_IdCliente ON Fact_Pagos (IdCliente);
CREATE INDEX IX_Fact_Satisfaccion_Fecha ON Fact_Satisfaccion (Fecha);
CREATE INDEX IX_Fact_Ventas_Fecha ON Fact_Ventas (Fecha);
CREATE INDEX IX_Fact_Ventas_IdCliente ON Fact_Ventas (IdCliente);
GO

-- Limpieza de duplicados en Fact_Ventas (después de la carga inicial)
-- Verificar la existencia de duplicados exactos en Fact_Ventas
SELECT 
    Fecha, ID_Comprobante, ID_Estimacion, IdCliente, IdFormaPago, ID_Temporada, ID_Campana_Promocion, Subtotal, Impuestos, Total, Precio_Total_Cotizacion,
    COUNT(*) AS Conteo_Duplicados
FROM Fact_Ventas
GROUP BY 
    Fecha, ID_Comprobante, ID_Estimacion, IdCliente, IdFormaPago, ID_Temporada, ID_Campana_Promocion, Subtotal, Impuestos, Total, Precio_Total_Cotizacion
HAVING COUNT(*) > 1;
GO

-- Eliminar duplicados exactos, manteniendo solo una instancia de cada fila única
WITH CTE_Duplicados AS (
    SELECT 
        *, 
        ROW_NUMBER() OVER (
            PARTITION BY 
                Fecha, ID_Comprobante, ID_Estimacion, IdCliente, IdFormaPago, ID_Temporada, ID_Campana_Promocion, Subtotal, Impuestos, Total, Precio_Total_Cotizacion 
            ORDER BY (SELECT NULL)
        ) AS Numero_Fila
    FROM Fact_Ventas
)
DELETE FROM CTE_Duplicados
WHERE Numero_Fila > 1;
GO

-- Verificar nuevamente después de la eliminación
SELECT 
    Fecha, ID_Comprobante, ID_Estimacion, IdCliente, IdFormaPago, ID_Temporada, ID_Campana_Promocion, Subtotal, Impuestos, Total, Precio_Total_Cotizacion,
    COUNT(*) AS Conteo_Duplicados
FROM Fact_Ventas
GROUP BY 
    Fecha, ID_Comprobante, ID_Estimacion, IdCliente, IdFormaPago, ID_Temporada, ID_Campana_Promocion, Subtotal, Impuestos, Total, Precio_Total_Cotizacion
HAVING COUNT(*) > 1;
GO

-- Opcionalmente, si los duplicados se basan en una clave única como ID_Comprobante
WITH CTE_Duplicados_Clave AS (
    SELECT 
        *, 
        ROW_NUMBER() OVER (
            PARTITION BY ID_Comprobante 
            ORDER BY Fecha DESC  -- Mantener el más reciente basado en Fecha
        ) AS Numero_Fila
    FROM Fact_Ventas
)
DELETE FROM CTE_Duplicados_Clave
WHERE Numero_Fila > 1;
GO