module.exports = {
  products: [
    { id: 'cpu-7600x', name: 'AMD Ryzen 5 7600X', category: 'Procesadores', price: 239, cost: 184, stock: 18, reorderPoint: 6, image: 'CPU', sales: 42 },
    { id: 'gpu-4060', name: 'NVIDIA RTX 4060 8GB', category: 'Tarjetas gráficas', price: 349, cost: 286, stock: 7, reorderPoint: 5, image: 'GPU', sales: 26 },
    { id: 'ram-32', name: 'Kingston Fury 32GB DDR5', category: 'Memoria RAM', price: 112, cost: 77, stock: 24, reorderPoint: 8, image: 'RAM', sales: 57 },
    { id: 'ssd-1tb', name: 'WD Black SN770 1TB NVMe', category: 'Almacenamiento', price: 86, cost: 56, stock: 3, reorderPoint: 6, image: 'SSD', sales: 63 },
    { id: 'mb-b650', name: 'MSI B650M Gaming WiFi', category: 'Placas madre', price: 166, cost: 124, stock: 11, reorderPoint: 4, image: 'MB', sales: 31 },
    { id: 'psu-750', name: 'Corsair RM750e 750W Gold', category: 'Fuentes', price: 119, cost: 81, stock: 15, reorderPoint: 5, image: 'PSU', sales: 35 }
  ],
  orders: [
    { id: 'ORD-1001', customer: 'María Torres', createdAt: '2026-10-22T14:00:00.000Z', items: [{ productId: 'cpu-7600x', quantity: 1, unitPrice: 239, unitCost: 184 }, { productId: 'ram-32', quantity: 1, unitPrice: 112, unitCost: 77 }] },
    { id: 'ORD-1002', customer: 'Diego Flores', createdAt: '2026-10-28T14:00:00.000Z', items: [{ productId: 'gpu-4060', quantity: 1, unitPrice: 349, unitCost: 286 }] }
  ]
};
