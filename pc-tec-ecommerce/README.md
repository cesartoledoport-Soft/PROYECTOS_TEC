# PC TEC — Plataforma E-Commerce y Analítica

Aplicación full-stack sin dependencias externas para comercializar componentes de hardware y seguir ventas, márgenes e inventario. El catálogo, el carrito y los indicadores usan la misma API REST.

## Funcionalidades

- Catálogo con búsqueda, filtro por categoría y disponibilidad de stock.
- Carrito persistente y creación de pedidos desde la API.
- Validación de cantidades, actualización de inventario y cálculo de margen bruto.
- Dashboard comercial con ventas, margen, inventario y ranking de productos.

## Ejecutar

Requiere Node.js 20+ (no hace falta instalar paquetes).

```bash
node src/server.js
# http://localhost:3000
```

`package.json` ofrece los equivalentes `npm start` y `npm test` cuando npm esté disponible. Para restablecer los datos de prueba, elimina `data/store.json` y reinicia. Para probar directamente: `node --test`.

## Endpoints

| Método | Ruta | Uso |
| --- | --- | --- |
| GET | `/api/products?search=&category=` | Catálogo |
| GET | `/api/categories` | Categorías |
| GET | `/api/analytics/summary` | KPIs y ranking |
| POST | `/api/orders` | Crea un pedido `{ customer, items }` |

## Power BI / Power Query

Power BI puede consumir `GET /api/analytics/summary` mediante **Obtener datos → Web**. En producción se recomienda sustituir el archivo local por PostgreSQL, autenticar los endpoints y conectar el modelo a una tabla de hechos de ventas.
