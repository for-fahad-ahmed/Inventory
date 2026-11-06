import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Dialog from "./Dialog.jsx";
import Button from "./Button.jsx";
import { getAllSuppliers } from "../api/suppliers.js";
import { getAllCategories } from "../api/categories.js";
import { CreateProduct } from "../api/products.js";

export default function AddProductDialog({ isOpen, onClose, onProductCreated }) {
  const navigate = useNavigate();

  const [suppliers, setSuppliers] = useState([]);
  const [suppliersLoading, setSuppliersLoading] = useState(false);
  const [suppliersError, setSuppliersError] = useState("");

  const [categories, setCategories] = useState([]);
  const [categoriesLoading, setCategoriesLoading] = useState(false);
  const [categoriesError, setCategoriesError] = useState("");

  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

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

  useEffect(() => {
    if (!isOpen) return;

    setError("");
    const loadDropdownData = async () => {
      await Promise.allSettled([fetchSuppliers(), fetchCategories()]);
    };

    loadDropdownData();
  }, [isOpen]);

  const handleAddProduct = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    const formData = new FormData(e.target);

    const cost_price = Number(formData.get("cost-price"));
    const selling_price = Number(formData.get("selling-price"));

    if (selling_price < cost_price) {
      setError("Selling price cannot be less than cost price.");
      setSubmitting(false);
      return;
    }

    const product = {
      name: formData.get("name")?.trim(),
      category_id: Number(formData.get("category")),
      supplier_id: Number(formData.get("supplier")),
      cost_price,
      selling_price,
      minimum_stock_lvl: Number(formData.get("min-stock-lvl")),
      description: formData.get("description")?.trim() || "",
    };

    try {
      const newProduct = await CreateProduct(product);
      e.target.reset();
      setError("");
      if (onProductCreated) {
        onProductCreated(newProduct);
      }
      onClose();
    } catch (err) {
      setError(err.message || "Failed to create product");
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setError("");
    onClose();
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={handleClose}
      title="Add Product"
      subtitle="Enter the details of your new product."
    >
      <form className="dialog-form" onSubmit={handleAddProduct}>
        {error && (
          <div className="form-error" role="alert">
            {error}
          </div>
        )}

        <div className="form-group">
          <label htmlFor="product-name">Product Name</label>
          <input
            id="product-name"
            name="name"
            type="text"
            placeholder="Enter product name"
            maxLength="50"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="product-category">Category</label>
          <select
            id="product-category"
            name="category"
            defaultValue=""
            required
            disabled={
              categoriesLoading || !!categoriesError || categories.length === 0
            }
          >
            {categoriesLoading ? (
              <option value="">Loading categories...</option>
            ) : categoriesError ? (
              <option value="">Failed to load categories</option>
            ) : categories.length === 0 ? (
              <option value="">No categories available</option>
            ) : (
              <>
                <option value="" disabled>
                  Select a category
                </option>

                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </>
            )}
          </select>

          {categoriesError && (
            <div className="field-error" role="alert">
              <span>{categoriesError}</span>
              <button
                type="button"
                className="retry-btn"
                onClick={fetchCategories}
              >
                Retry
              </button>
            </div>
          )}

          <div className="field-helper">
            <span>If a category is not available, please create it first.</span>
            <button
              type="button"
              className="helper-action-btn"
              onClick={() => navigate("/settings")}
            >
              + Add Category
            </button>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="product-supplier">Supplier</label>
          <select
            id="product-supplier"
            name="supplier"
            defaultValue=""
            required
            disabled={
              suppliersLoading || !!suppliersError || suppliers.length === 0
            }
          >
            {suppliersLoading ? (
              <option value="">Loading suppliers...</option>
            ) : suppliersError ? (
              <option value="">Failed to load suppliers</option>
            ) : suppliers.length === 0 ? (
              <option value="">No suppliers available</option>
            ) : (
              <>
                <option value="" disabled>
                  Select a supplier
                </option>

                {suppliers.map((supplier) => (
                  <option key={supplier.id} value={supplier.id}>
                    {supplier.name}
                  </option>
                ))}
              </>
            )}
          </select>

          {suppliersError && (
            <div className="field-error" role="alert">
              <span>{suppliersError}</span>
              <button
                type="button"
                className="retry-btn"
                onClick={fetchSuppliers}
              >
                Retry
              </button>
            </div>
          )}

          <div className="field-helper">
            <span>If a supplier is not available, please create it first.</span>
            <button
              type="button"
              className="helper-action-btn"
              onClick={() => navigate("/suppliers")}
            >
              + Add Supplier
            </button>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="product-cost-price">Cost Price</label>
          <input
            id="product-cost-price"
            name="cost-price"
            type="number"
            min="0"
            step="0.01"
            placeholder="Enter price"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="product-selling-price">Selling Price</label>
          <input
            id="product-selling-price"
            name="selling-price"
            type="number"
            min="0.01"
            step="0.01"
            placeholder="Enter price"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="product-min-stock-lvl">Minimum Stock Level</label>
          <input
            id="product-min-stock-lvl"
            name="min-stock-lvl"
            type="number"
            min="0"
            step="1"
            placeholder="Enter Minimum Stock Level"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="product-description">Description</label>
          <textarea
            id="product-description"
            name="description"
            placeholder="Enter product description"
            maxLength="150"
            rows="3"
          />
        </div>

        <div className="dialog-actions">
          <Button type="button" onClick={handleClose}>
            Cancel
          </Button>

          <Button type="submit" disabled={submitting}>
            {submitting ? "Adding..." : "Add Product"}
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
