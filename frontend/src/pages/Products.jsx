import { useEffect, useState } from "react";
import "../styles/Product.css";
import Button from "../components/Button.jsx";
import AddProductDialog from "../components/AddProductDialog.jsx";
import Toast from "../components/Toast.jsx";
import { getInventory } from "../api/inventory.js";
import DataTable from "../components/DataTable.jsx";
import PageHeader from "../components/PageHeader.jsx";
import Pagination from "../components/Pagination.jsx";
import { getAllCategories } from "../api/categories.js";
import { getAllSuppliers } from "../api/suppliers.js";

const productColumns = [
  { key: "product_code", label: "Product Code", mono: true },
  { key: "name", label: "Product Name" },
  { key: "description", label: "Description" },
  { key: "quantity_on_hand", label: "Available Stock", align: "right" },
  { key: "minimum_stock_lvl", label: "Minimum Stock", align: "right" },
  { key: "cost_price", label: "Cost Price", align: "right" },
  { key: "selling_price", label: "Selling Price", align: "right" },
];
export default function Products() {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [toast, setToast] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [products, setProducts] = useState([]);

  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  const [categories, setCategories] = useState([]);
  const [categoriesLoading, setCategoriesLoading] = useState(false);
  const [categoriesError, setCategoriesError] = useState("");

  const [suppliers, setSuppliers] = useState([]);
  const [suppliersLoading, setSuppliersLoading] = useState(false);
  const [suppliersError, setSuppliersError] = useState("");

  const [activeOnly, setActiveOnly] = useState(true);
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [filters, setFilters] = useState({
    categoryId: null,
    supplierId: null,
    activeOnly: true,
    lowStockOnly: false,
    search: "",
  });

  const handleSearch = (e) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const categoryVal = formData.get("category");
    const supplierVal = formData.get("suppliers");
    const searchVal = formData.get("search") || "";

    setPage(1);
    setFilters({
      categoryId: categoryVal ? Number(categoryVal) : null,
      supplierId: supplierVal ? Number(supplierVal) : null,
      activeOnly,
      lowStockOnly,
      search: searchVal.toString(),
    });
  };

  const handleLimitChange = (newLimit) => {
    setLimit(newLimit);
    setPage(1);
  };

  const fetchCategories = async () => {
    try {
      setCategoriesLoading(true);
      setCategoriesError("");

      const data = await getAllCategories();
      setCategories(Array.isArray(data) ? data : []);
    } catch (err) {
      setCategoriesError(err.message || "Failed to load categories");
    } finally {
      setCategoriesLoading(false);
    }
  };

  const fetchSuppliers = async () => {
    try {
      setSuppliersLoading(true);
      setSuppliersError("");

      const data = await getAllSuppliers();
      setSuppliers(Array.isArray(data) ? data : []);
    } catch (err) {
      setSuppliersError(err.message || "Failed to load suppliers");
    } finally {
      setSuppliersLoading(false);
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");

      const skip = (page - 1) * limit;
      const data = await getInventory(
        limit,
        skip,
        filters.activeOnly,
        filters.categoryId,
        filters.supplierId,
        filters.lowStockOnly,
        filters.search,
      );

      const items = Array.isArray(data?.products) ? data.products : [];
      setProducts(items);
      setTotal(data?.total ?? items.length);
      setHasMore(Boolean(data?.has_more));
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    const loadDropdownData = async () => {
      await Promise.allSettled([fetchCategories(), fetchSuppliers()]);
    };

    loadDropdownData();
  }, []);

  useEffect(() => {
    fetchData();
  }, [page, limit, filters]);

  const formattedProducts = products.map((item, index) => ({
    id: item.product_id ?? item.product?.id ?? index,
    product_code: item.product?.product_code,
    name: item.product?.name,
    description: item.product?.description || "—",
    quantity_on_hand: item.quantity_on_hand,
    minimum_stock_lvl: item.product?.minimum_stock_lvl,
    cost_price: Number(item.product?.cost_price ?? 0).toFixed(2),
    selling_price: Number(item.product?.selling_price ?? 0).toFixed(2),
  }));

  let content;

  if (loading) {
    content = <p>Loading...</p>;
  } else if (error) {
    content = <p className="error">{error}</p>;
  } else if (products.length === 0) {
    content = <p>No products found</p>;
  } else {
    content = <DataTable columns={productColumns} data={formattedProducts} />;
  }

  const handleProductCreated = (newProduct) => {
    setToast({
      message: `Product "${newProduct?.name || "Item"}" created successfully!`,
      type: "success",
    });
    fetchData();
  };

  let categoryOptions;

  if (categoriesLoading) {
    categoryOptions = <option value="">Loading categories...</option>;
  } else if (categoriesError) {
    categoryOptions = <option value="">Failed to load categories</option>;
  } else if (categories.length === 0) {
    categoryOptions = <option value="">No categories available</option>;
  } else {
    categoryOptions = (
      <>
        <option value="">All categories</option>

        {categories.map((category) => (
          <option key={category.id} value={category.id}>
            {category.name}
          </option>
        ))}
      </>
    );
  }

  let supplierOptions;

  if (suppliersLoading) {
    supplierOptions = <option value="">Loading suppliers...</option>;
  } else if (suppliersError) {
    supplierOptions = <option value="">Failed to load suppliers</option>;
  } else if (suppliers.length === 0) {
    supplierOptions = <option value="">No suppliers available</option>;
  } else {
    supplierOptions = (
      <>
        <option value="">All suppliers</option>

        {suppliers.map((supplier) => (
          <option key={supplier.id} value={supplier.id}>
            {supplier.name}
          </option>
        ))}
      </>
    );
  }

  return (
    <div className="products">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      <PageHeader
        title="Products"
        subtitle="Browse and manage your product catalog"
        actionLabel="+ Add Product"
        onAction={() => setIsDialogOpen(true)}
      >
        <form className="search-form" onSubmit={handleSearch}>
          <div className="filter-field">
            <label htmlFor="category">Category</label>
            <select
              id="category"
              name="category"
              defaultValue=""
              disabled={
                categoriesLoading ||
                !!categoriesError ||
                categories.length === 0
              }
            >
              {categoryOptions}
            </select>
          </div>

          <div className="filter-field">
            <label htmlFor="suppliers">Supplier</label>
            <select
              id="suppliers"
              name="suppliers"
              defaultValue=""
              disabled={
                suppliersLoading || !!suppliersError || suppliers.length === 0
              }
            >
              {supplierOptions}
            </select>
          </div>

          <div className="filter-toggles">
            <label className="checkbox-filter">
              <input
                type="checkbox"
                checked={activeOnly}
                onChange={(e) => setActiveOnly(e.target.checked)}
              />
              <span>Active Only</span>
            </label>

            <label className="checkbox-filter">
              <input
                type="checkbox"
                checked={lowStockOnly}
                onChange={(e) => setLowStockOnly(e.target.checked)}
              />
              <span>Low Stock</span>
            </label>
          </div>

          <div className="search-input-group">
            <input
              type="text"
              name="search"
              placeholder="Search products..."
              aria-label="Search"
            />
            <Button type="submit" variant="secondary">
              Search
            </Button>
          </div>
        </form>
      </PageHeader>

      <AddProductDialog
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        onProductCreated={handleProductCreated}
      />

      <div className="products-table-container">
        <div className="table-scroll-wrapper">{content}</div>

        {!loading && !error && products.length > 0 && (
          <Pagination
            page={page}
            limit={limit}
            total={total}
            currentCount={products.length}
            hasMore={hasMore}
            onPageChange={setPage}
            onLimitChange={handleLimitChange}
            itemLabel="products"
            disabled={loading}
          />
        )}
      </div>
    </div>
  );
}
