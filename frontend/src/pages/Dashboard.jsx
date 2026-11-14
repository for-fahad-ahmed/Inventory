import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import "../styles/Dashboard.css";
import Button from "../components/Button.jsx";
import AddProductDialog from "../components/AddProductDialog.jsx";
import DataTable from "../components/DataTable.jsx";
import { getLowStockProducts } from "../api/inventory.js";

const lowStockColumns = [
  { key: "product_code", label: "Product Code", mono: true },
  { key: "name", label: "Product Name" },
  { key: "quantity_on_hand", label: "Available Stock", align: "right" },
  { key: "minimum_stock_lvl", label: "Minimum Stock", align: "right" },
  { key: "selling_price", label: "Selling Price", align: "right" },
];

export default function Dashboard() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [lowStockProducts, setLowStockProducts] = useState([]);
  const [isAddProductOpen, setIsAddProductOpen] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError("");

        const products = await getLowStockProducts();
        setLowStockProducts(products);
      } catch (err) {
        setError(err.message || "Something went wrong");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formattedLowStockData = lowStockProducts.map((item, index) => ({
    id: item.product_id ?? item.id ?? item.product?.id ?? index,
    product_code: item.product?.product_code,
    name: item.product?.name,
    quantity_on_hand: item.quantity_on_hand,
    minimum_stock_lvl: item.product?.minimum_stock_lvl,
    selling_price: Number(item.product?.selling_price ?? 0).toFixed(2),
  }));

  let lowStockContent;

  if (loading) {
    lowStockContent = <p>Loading...</p>;
  } else if (error) {
    lowStockContent = <p className="error">{error}</p>;
  } else if (lowStockProducts.length === 0) {
    lowStockContent = <p>No low stock products found</p>;
  } else {
    lowStockContent = (
      <DataTable columns={lowStockColumns} data={formattedLowStockData} />
    );
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      <div className="main-cards">
        <div className="card">
          <h2>Products</h2>
          <p>Manage your inventory</p>
          <Link to="/products" className="card-link">
            View Products
          </Link>
        </div>

        <div className="card">
          <h2>Customers</h2>
          <p>Manage your customers</p>
          <Link to="/customers" className="card-link">
            View customers
          </Link>
        </div>

        <div className="card">
          <h2>Purchases</h2>
          <p>Manage purchases</p>
          <Link to="/purchases" className="card-link">
            View purchases
          </Link>
        </div>

        <div className="card">
          <h2>Sales</h2>
          <p>Manage Sales</p>
          <Link to="/sales" className="card-link">
            View sales
          </Link>
        </div>
      </div>

      <div className="quick-actions">
        <h2>Quick Actions</h2>

        <div className="buttons">
          <Button
            type="button"
            variant="primary"
            onClick={() => setIsAddProductOpen(true)}
          >
            + Add Product
          </Button>

          <Button type="button" variant="secondary">
            + Record Purchase
          </Button>

          <Button type="button" variant="secondary">
            + New Sale
          </Button>
        </div>
      </div>

      <div className="card low-stock-items">
        <h2>Low Stock Items</h2>
        {lowStockContent}
      </div>

      <AddProductDialog
        isOpen={isAddProductOpen}
        onClose={() => setIsAddProductOpen(false)}
      />
    </div>
  );
}
