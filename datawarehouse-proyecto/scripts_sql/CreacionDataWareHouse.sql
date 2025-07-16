-- Crear la base de datos del Data Warehouse
USE master;
GO
CREATE DATABASE DataWarahouse;
GO
USE DataWarahouse;
GO

-- Crear dimensiones independientes para cada data mart para evitar relaciones entre marts
-- Esto mantiene la normalización dentro de cada mart (evitando redundancia interna), pero los marts son independientes

-- Dimensiones para Hechos_Pago
CREATE TABLE Dim_Cliente_Pago (
    IdCliente INT PRIMARY KEY,
    Nombre VARCHAR(100),
    Apellidos VARCHAR(100),
    Correo VARCHAR(100),
    Telefono VARCHAR(20),
    Nacionalidad VARCHAR(20),
    TipoCliente VARCHAR(50),
    FechaRegistro DATE,
    Actividad_Economica VARCHAR(255)
);

CREATE TABLE Dim_Forma_Pago_Pago (
    IdFormaPago INT PRIMARY KEY,
    TipoFormaPago VARCHAR(50),
    EntidadBancaria VARCHAR(50),
    TipoTarjeta VARCHAR(50)
);

CREATE TABLE Dim_Habitacion_Pago (
    IdHabitacion INT PRIMARY KEY,
    Numero_Habitacion INT,
    TipoHabitacion VARCHAR(50),
    Capacidad INT,
    PrecioBase DECIMAL(10,2)
);

CREATE TABLE Dim_Reserva_Pago (
    IdReserva INT PRIMARY KEY,
    FechaReserva DATE,
    FechaCheckin DATE,
    FechaCheckout DATE,
    EstadoReserva VARCHAR(50),
    NumeroNoches INT,
    OrigenReserva VARCHAR(50)
);

CREATE TABLE Dim_Empleado_Pago (
    IdEmpleado INT PRIMARY KEY,
    Nombres VARCHAR(100),
    Apellidos VARCHAR(100),
    Puesto VARCHAR(50),
    Departamento VARCHAR(50)
);

-- Dimensiones para Hecho_Satisfaccion (no comparte con otros marts)
CREATE TABLE Dim_CanalAtencion_Satisfaccion (
    CanalAtencionID INT PRIMARY KEY,
    NombreCanal VARCHAR(100),
    Descripcion VARCHAR(255),
    HorarioAtencion VARCHAR(100),
    Responsable VARCHAR(100)
);

CREATE TABLE Dim_MotivoInsatisfaccion_Satisfaccion (
    MotivoInsatisfaccionID INT PRIMARY KEY,
    Categoria VARCHAR(100),
    DescripcionMotivo VARCHAR(255),
    NivelGravedad VARCHAR(50)
);

CREATE TABLE Dim_TipoCliente_Satisfaccion (
    TipoClienteID INT PRIMARY KEY,
    NombreTipoCliente VARCHAR(100)
);

CREATE TABLE Dim_TipoHabitacion_Satisfaccion (
    ID_Tipo_Habitacion INT PRIMARY KEY,
    Nombre_Tipo_Habitacion VARCHAR(100),
    Descripcion VARCHAR(MAX),
    Estado VARCHAR(20)
);

CREATE TABLE Dim_TipoQueja_Satisfaccion (
    TipoQuejaID INT PRIMARY KEY,
    NombreTipoQueja VARCHAR(100),
    Descripcion VARCHAR(255)
);

CREATE TABLE Dim_TipoServicio_Satisfaccion (
    TipoServicioID INT PRIMARY KEY,
    NombreServicio VARCHAR(100),
    Descripcion VARCHAR(255),
    Estado VARCHAR(20)
);

-- Dimensiones para Hechos_Ventas (no comparte con otros marts)
CREATE TABLE Dim_Cliente_Ventas (
    IdCliente INT PRIMARY KEY,
    Nombre VARCHAR(100),
    Apellidos VARCHAR(100),
    Correo VARCHAR(100),
    Telefono VARCHAR(20),
    Nacionalidad VARCHAR(20),
    TipoCliente VARCHAR(50),
    FechaRegistro DATE
);

CREATE TABLE Dim_Forma_Pago_Ventas (
    IdFormaPago INT PRIMARY KEY,
    TipoFormaPago VARCHAR(50),
    EntidadBancaria VARCHAR(50)
);

CREATE TABLE Dim_Periodo_Ventas (
    ID_Temporada INT PRIMARY KEY,
    Nombre_Temporada VARCHAR(100),
    Fecha_Inicio_Temporada DATE,
    Fecha_Fin_Temporada DATE,
    Factor_Precio_Temporada DECIMAL(10,2)
);

CREATE TABLE Dim_Estimacion_Ventas (
    ID_Estimacion INT PRIMARY KEY,
    Fecha_Cotizacion DATE,
    ID_Cliente INT,
    Numero_Adultos INT,
    Numero_Ninos INT,
    ID_Tipo_Habitacion INT,
    Cantidad_Habitaciones INT,
    Servicios_Adicionales VARCHAR(MAX),
    Precio_Total DECIMAL(10,2),
    Estado VARCHAR(50),
    ID_Medio_Contacto INT
);

CREATE TABLE Dim_Comprobante_Ventas (
    ID_Comprobante INT PRIMARY KEY,
    ID_Reserva INT,
    Fecha_Comprobante DATE,
    Numero_Comprobante VARCHAR(255),
    ID_Cliente INT,
    Subtotal DECIMAL(10,2),
    Impuestos DECIMAL(10,2),
    Total DECIMAL(10,2),
    ID_Forma_Pago INT,
    ID_Medio_Pago INT
);

CREATE TABLE Dim_Campana_Promocion_Ventas (
    ID_Campana_Promocion INT PRIMARY KEY,
    Nombre_Campana_Promocion VARCHAR(100),
    ID_Temporada INT,
    Fecha_Inicio DATE,
    Fecha_Fin DATE,
    Objetivo_Campana_Promocion VARCHAR(200),
    Justificacion_Campana VARCHAR(500),
    Nombre_Canal_Promocion VARCHAR(100),
    Descripcion_Canal_Promocion VARCHAR(500)
);

-- Crear tablas de hechos independientes
CREATE TABLE Fact_Pagos (
    Fecha DATE,
    IdCliente INT,
    IdHabitacion INT,
    IdReserva INT,
    IdFormaPago INT,
    IdEmpleado INT,
    monto_pago DECIMAL(10,2),
    descuento DECIMAL(10,2),
    impuestos DECIMAL(10,2),
    total_factura DECIMAL(10,2),
    FOREIGN KEY (IdCliente) REFERENCES Dim_Cliente_Pago(IdCliente),
    FOREIGN KEY (IdHabitacion) REFERENCES Dim_Habitacion_Pago(IdHabitacion),
    FOREIGN KEY (IdReserva) REFERENCES Dim_Reserva_Pago(IdReserva),
    FOREIGN KEY (IdFormaPago) REFERENCES Dim_Forma_Pago_Pago(IdFormaPago),
    FOREIGN KEY (IdEmpleado) REFERENCES Dim_Empleado_Pago(IdEmpleado)
);

CREATE TABLE Fact_Satisfaccion (
    Fecha DATE,
    TipoClienteID INT,
    ID_Tipo_Habitacion INT,
    TipoServicioID INT,
    TipoQuejaID INT,
    CanalAtencionID INT,
    MotivoInsatisfaccionID INT,
    NivelSatisfaccion INT,
    Resuelto BIT,
    FOREIGN KEY (TipoClienteID) REFERENCES Dim_TipoCliente_Satisfaccion(TipoClienteID),
    FOREIGN KEY (ID_Tipo_Habitacion) REFERENCES Dim_TipoHabitacion_Satisfaccion(ID_Tipo_Habitacion),
    FOREIGN KEY (TipoServicioID) REFERENCES Dim_TipoServicio_Satisfaccion(TipoServicioID),
    FOREIGN KEY (TipoQuejaID) REFERENCES Dim_TipoQueja_Satisfaccion(TipoQuejaID),
    FOREIGN KEY (CanalAtencionID) REFERENCES Dim_CanalAtencion_Satisfaccion(CanalAtencionID),
    FOREIGN KEY (MotivoInsatisfaccionID) REFERENCES Dim_MotivoInsatisfaccion_Satisfaccion(MotivoInsatisfaccionID)
);

CREATE TABLE Fact_Ventas (
    Fecha DATE,
    ID_Comprobante INT,
    ID_Estimacion INT,
    IdCliente INT,
    IdFormaPago INT,
    ID_Temporada INT,
    ID_Campana_Promocion INT,
    Subtotal DECIMAL(10,2),
    Impuestos DECIMAL(10,2),
    Total DECIMAL(10,2),
    Precio_Total_Cotizacion DECIMAL(10,2),
    FOREIGN KEY (ID_Comprobante) REFERENCES Dim_Comprobante_Ventas(ID_Comprobante),
    FOREIGN KEY (ID_Estimacion) REFERENCES Dim_Estimacion_Ventas(ID_Estimacion),
    FOREIGN KEY (IdCliente) REFERENCES Dim_Cliente_Ventas(IdCliente),
    FOREIGN KEY (IdFormaPago) REFERENCES Dim_Forma_Pago_Ventas(IdFormaPago),
    FOREIGN KEY (ID_Temporada) REFERENCES Dim_Periodo_Ventas(ID_Temporada),
    FOREIGN KEY (ID_Campana_Promocion) REFERENCES Dim_Campana_Promocion_Ventas(ID_Campana_Promocion)
);