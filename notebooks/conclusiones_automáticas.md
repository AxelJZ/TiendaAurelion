# Conclusiones y Hallazgos - Proyecto Análisis de Medios de Pago


## Resumen numérico
- Total facturado: $2,624,009.00
- Número de registros (líneas de detalle): 343
- Número de ventas únicas (id_venta): 120
- Número de outliers detectados en 'importe' (IQR): 7
- Ticket promedio por venta (general): $21,866.74

### Tabla resumen por medio de pago

| medio         |   n_transacciones |   pct_transacciones |   importe_total |   pct_importe |   ticket_promedio |
|:--------------|------------------:|--------------------:|----------------:|--------------:|------------------:|
| efectivo      |               111 |               32.36 |          934819 |         35.63 |           8421.79 |
| qr            |                91 |               26.53 |          689774 |         26.29 |           7928.44 |
| transferencia |                72 |               20.99 |          542219 |         20.66 |           7530.82 |
| tarjeta       |                69 |               20.12 |          457197 |         17.42 |           6723.49 |


## Hallazgos clave
- El medio con **mayor número de transacciones** es **efectivo** con **32.36%** de las operaciones.
- El medio que **contribuye más al importe total** es **efectivo**, aportando **35.63%** del facturado.
- El **ticket promedio más alto** corresponde a **efectivo** (≈ $8421.79), mientras que el más bajo es **tarjeta** (≈ $6723.49).
- El mes con mayor facturación fue **2024-05** con un total de **$561,832.00**.
- El cambio porcentual del total facturado entre el primer mes (2024-01) y el último (2024-06) es **-3.74%**.
- Outliers: se detectaron **7** registros con importe por encima del límite IQR superior. Recomendación: inspección manual de esos registros antes de decidir limpieza.


## Recomendaciones operativas y comerciales (sugeridas)
1. Si el objetivo es aumentar el ticket promedio, considerar promociones para el medio **efectivo**.
2. Si el foco es aumentar la cantidad de operaciones, diseñar campañas que incentiven el medio **efectivo**.
3. Analizar con detalle los 7 outliers: confirmar si son clientes VIP o errores.
4. Si algún medio muestra crecimiento sostenido, evaluar campañas que aprovechen esa tendencia.

## Tendencias por medio de pago (primer vs último mes)
- tarjeta: ↑ cambio 13.07% (de $79,462.00 a $89,846.00).
- qr: ↑ cambio 135.66% (de $76,000.00 a $179,102.00).
- transferencia: ↓ cambio -57.85% (de $142,054.00 a $59,882.00).
- efectivo: ↓ cambio -22.01% (de $232,324.00 a $181,185.00).



## Próximo sprint - Extensiones recomendadas
1. Segmentación RFM (Recencia, Frecuencia, Valor): identificar clientes VIP y perfiles por medio de pago.
2. Modelo de predicción simple: predecir medio de pago probable por transacción usando features (importe, categoría, ciudad, día).
3. Test A/B de incentivos: diseñar experimentos para probar promociones por medio de pago (ej.: descuento por pago con transferencia).
4. Dashboard interactivo (Streamlit / Dash): visualizaciones dinámicas para ventas, medios y segmentos.
5. Validación de calidad de datos: pipeline automatizado para detectar y corregir recategorizaciones y precios inconsistentes.
