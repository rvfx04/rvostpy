DECLARE @F1 DATE = '2025-05-01';
DECLARE @F2 DATE = '2025-12-31';
DECLARE @cols NVARCHAR(MAX), 
        @cols_isnull NVARCHAR(MAX),
        @cols_with_isnull NVARCHAR(MAX),
        @cols_op NVARCHAR(MAX),
        @sql NVARCHAR(MAX);

-- Obtener columnas de clientes con ISNULL y columnas para OPs
SELECT 
    @cols = STRING_AGG(QUOTENAME(LEFT(d.NommaeAnexoCliente, 15)), ','),
    @cols_isnull = STRING_AGG('ISNULL(' + QUOTENAME(LEFT(d.NommaeAnexoCliente, 15)) + ', 0)', ' + '),
    @cols_with_isnull = STRING_AGG('ISNULL(' + QUOTENAME(LEFT(d.NommaeAnexoCliente, 15)) + ', 0) AS ' + QUOTENAME(LEFT(d.NommaeAnexoCliente, 15)), ', '),
    @cols_op = STRING_AGG('ISNULL(' + QUOTENAME(LEFT(d.NommaeAnexoCliente, 15) + '_OP') + ', '''') AS ' + QUOTENAME(LEFT(d.NommaeAnexoCliente, 15) + '_OP'), ', ')
FROM (
    SELECT DISTINCT LEFT(d.NommaeAnexoCliente, 15) AS NommaeAnexoCliente
    FROM dbo.docNotaInventario a
    INNER JOIN dbo.docNotaInventarioItem b 
        ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario AND b.dCantidadIng <> 0
    INNER JOIN dbo.docOrdenProduccion c 
        ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion 
        AND c.bCerrado = 0 AND c.bAnulado = 0 AND c.IdtdDocumentoForm = 127
    INNER JOIN dbo.maeAnexoCliente d 
        ON c.IdmaeAnexo_Cliente = d.IdmaeAnexo_Cliente
    WHERE a.IdtdDocumentoForm = 131
        AND a.bDevolucion = 0 
        AND a.bDesactivado = 0 
        AND a.bAnulado = 0 
        AND a.IdDocumento_OrdenProduccion <> 0 
        AND a.dtFechaRegistro BETWEEN @F1 AND @F2
        AND a.IdmaeCentroCosto = 29
) d;

-- Crear columnas para el PIVOT de OPs
DECLARE @cols_pivot_op NVARCHAR(MAX);
SELECT @cols_pivot_op = STRING_AGG(QUOTENAME(LEFT(d.NommaeAnexoCliente, 15) + '_OP'), ',')
FROM (
    SELECT DISTINCT LEFT(d.NommaeAnexoCliente, 15) AS NommaeAnexoCliente
    FROM dbo.docNotaInventario a
    INNER JOIN dbo.docNotaInventarioItem b 
        ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario AND b.dCantidadIng <> 0
    INNER JOIN dbo.docOrdenProduccion c 
        ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion 
        AND c.bCerrado = 0 AND c.bAnulado = 0 AND c.IdtdDocumentoForm = 127
    INNER JOIN dbo.maeAnexoCliente d 
        ON c.IdmaeAnexo_Cliente = d.IdmaeAnexo_Cliente
    WHERE a.IdtdDocumentoForm = 131
        AND a.bDevolucion = 0 
        AND a.bDesactivado = 0 
        AND a.bAnulado = 0 
        AND a.IdDocumento_OrdenProduccion <> 0 
        AND a.dtFechaRegistro BETWEEN @F1 AND @F2
        AND a.IdmaeCentroCosto = 29
) d;

-- Crear la consulta dinámica usando parámetros
SET @sql = N'
WITH DatosCantidad AS (
    SELECT 
        
		CONVERT(varchar(10), a.dtFechaRegistro, 105) AS FECHA,
        LEFT(d.NommaeAnexoCliente, 15) AS CLIENTE,
        CAST(b.dCantidadIng AS INT) AS UNID
    FROM dbo.docNotaInventario a
    INNER JOIN dbo.docNotaInventarioItem b 
        ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario AND b.dCantidadIng <> 0
    INNER JOIN dbo.docOrdenProduccion c 
        ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion 
        AND c.bCerrado = 0 AND c.bAnulado = 0 AND c.IdtdDocumentoForm = 127
    INNER JOIN dbo.maeAnexoCliente d 
        ON c.IdmaeAnexo_Cliente = d.IdmaeAnexo_Cliente
    WHERE a.IdtdDocumentoForm = 131
        AND a.bDevolucion = 0 
        AND a.bDesactivado = 0 
        AND a.bAnulado = 0 
        AND a.IdDocumento_OrdenProduccion <> 0 
        AND a.dtFechaRegistro BETWEEN @pF1 AND @pF2
        AND a.IdmaeCentroCosto = 29
),
DatosOP AS (
    SELECT 
        FECHA,
        NommaeAnexoCliente + ''_OP'' AS CLIENTE_OP,
        STRING_AGG(CoddocOrdenProduccion, '', '') AS OPS
    FROM (
        SELECT DISTINCT 
			CONVERT(varchar(10), a.dtFechaRegistro, 105) AS FECHA,
        
            LEFT(d.NommaeAnexoCliente, 15) AS NommaeAnexoCliente,
            c.CoddocOrdenProduccion
        FROM dbo.docNotaInventario a
        INNER JOIN dbo.docNotaInventarioItem b 
            ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario AND b.dCantidadIng <> 0
        INNER JOIN dbo.docOrdenProduccion c 
            ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion 
            AND c.bCerrado = 0 AND c.bAnulado = 0 AND c.IdtdDocumentoForm = 127
        INNER JOIN dbo.maeAnexoCliente d 
            ON c.IdmaeAnexo_Cliente = d.IdmaeAnexo_Cliente
        WHERE a.IdtdDocumentoForm = 131
            AND a.bDevolucion = 0 
            AND a.bDesactivado = 0 
            AND a.bAnulado = 0 
            AND a.IdDocumento_OrdenProduccion <> 0 
            AND a.dtFechaRegistro BETWEEN @pF1 AND @pF2
            AND a.IdmaeCentroCosto = 29
    ) subquery
    GROUP BY FECHA, NommaeAnexoCliente
),
PivotCantidad AS (
    SELECT FECHA, ' + @cols + '
    FROM DatosCantidad
    PIVOT (SUM(UNID) FOR CLIENTE IN (' + @cols + ')) AS PivotTable
),
PivotOP AS (
    SELECT FECHA, ' + @cols_pivot_op + '
    FROM DatosOP
    PIVOT (MAX(OPS) FOR CLIENTE_OP IN (' + @cols_pivot_op + ')) AS PivotTable
)
SELECT 
    p1.FECHA, 
    ' + @cols_with_isnull + ', 
	' + @cols_isnull + ' AS TOTAL,
    ' + @cols_op + '
    
FROM PivotCantidad p1
LEFT JOIN PivotOP p2 ON p1.FECHA = p2.FECHA
ORDER BY p1.FECHA;';

-- Ejecutar la consulta dinámica con parámetros
EXEC sp_executesql @sql, N'@pF1 DATE, @pF2 DATE', @pF1 = @F1, @pF2 = @F2;
