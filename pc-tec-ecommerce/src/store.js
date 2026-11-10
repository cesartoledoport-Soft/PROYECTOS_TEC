const fs = require('node:fs');
const path = require('node:path');
const seed = require('./seed');
const dataPath = path.join(__dirname, '..', 'data', 'store.json');
function ensureStore() { if (!fs.existsSync(dataPath)) { fs.mkdirSync(path.dirname(dataPath), { recursive: true }); fs.writeFileSync(dataPath, JSON.stringify(seed, null, 2)); } }
function read() { ensureStore(); return JSON.parse(fs.readFileSync(dataPath, 'utf8')); }
function write(state) { fs.writeFileSync(dataPath, JSON.stringify(state, null, 2)); }
function getProducts(filters = {}) { const search = (filters.search || '').toLowerCase(); return read().products.filter(p => (!filters.category || p.category === filters.category) && (!search || `${p.name} ${p.category}`.toLowerCase().includes(search))); }
function createOrder({ customer, items }) {
  if (!customer || !Array.isArray(items) || !items.length) throw new Error('El cliente y al menos un producto son obligatorios.');
  const state = read(); const normalized = items.map(item => { const product = state.products.find(p => p.id === item.productId); const quantity = Number(item.quantity); if (!product) throw new Error(`Producto no encontrado: ${item.productId}`); if (!Number.isInteger(quantity) || quantity < 1) throw new Error('La cantidad debe ser un entero positivo.'); if (product.stock < quantity) throw new Error(`Stock insuficiente para ${product.name}.`); return { product, quantity }; });
  const order = { id: `ORD-${Date.now().toString().slice(-8)}`, customer: customer.trim(), createdAt: new Date().toISOString(), items: normalized.map(({ product, quantity }) => ({ productId: product.id, quantity, unitPrice: product.price, unitCost: product.cost })) };
  normalized.forEach(({ product, quantity }) => { product.stock -= quantity; product.sales += quantity; }); state.orders.push(order); write(state); return order;
}
function summary() { const state = read(); const sales = state.orders.flatMap(order => order.items); const revenue = sales.reduce((n,i) => n + i.quantity * i.unitPrice, 0); const grossProfit = sales.reduce((n,i) => n + i.quantity * (i.unitPrice - i.unitCost), 0); const inventoryValue = state.products.reduce((n,p) => n + p.stock * p.cost, 0); const lowStock = state.products.filter(p => p.stock <= p.reorderPoint); const ranking = state.products.map(p => ({ name:p.name, units:p.sales, revenue:p.sales*p.price, marginPct:Number(((p.price-p.cost)/p.price*100).toFixed(1)) })).sort((a,b)=>b.revenue-a.revenue); return { kpis:{ revenue, grossProfit, marginPct: revenue ? Number((grossProfit/revenue*100).toFixed(1)) : 0, inventoryValue, lowStockCount:lowStock.length }, lowStock, ranking, generatedAt:new Date().toISOString() }; }
module.exports = { getProducts, createOrder, summary, read, write };
