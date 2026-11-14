import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Dialog from "./Dialog.jsx";
import Button from "./Button.jsx";
import { getAllSuppliers } from "../api/suppliers.js";
import { getAllCategories } from "../api/categories.js";
import { CreateProduct, UpdateProduct } from "../api/products.js";

export default function ProductDialog({
  isOpen,
  onClose,
  product = null,
  onProductCreated,
  onProductUpdated,
}) {
  const navigate = useNavigate();
  const isEditMode = Boolean(product);

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

  const handleSubmit = async (e) => {
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

    const payload = {
      name: formData.get("name")?.trim(),
      category_id: Number(formData.get("category")),
      supplier_id: Number(formData.get("supplier")),
      cost_price,
      selling_price,
      minimum_stock_lvl: Number(formData.get("min-stock-lvl")),
      description: formData.get("description")?.trim() || "",
    };

    try {
      if (isEditMode) {
        const updatedProduct = await UpdateProduct(product.id, payload);
        setError("");
        onProductUpdated?.(updatedProduct);
        onClose();
      } else {
        const newProduct = await CreateProduct(payload);
        e.target.reset();
        setError("");
        onProductCreated?.(newProduct);
        onClose();
      }
    } catch (err) {
      setError(
        err.message ||
          (isEditMode ? "Failed to update product" : "Failed to create product"),
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setError("");
    onClose();
  };

  const initialDescription = isEditMode
    ? (product.raw_description ??
      (product.description === "—" ? "" : product.description) ??
      "")
    : "";

  return (
    <Dialog
      isOpen={isOpen}
      onClose={handleClose}
      title={isEditMode ? "Edit Product" : "Add Product"}
      subtitle={
        isEditMode
          ? `Update the details for ${product.name || "this product"}.`
          : "Enter the details of your new product."
      }
    >
      <form
        key={isEditMode ? `edit-${product.id}` : "add"}
        className="dialog-form"
        onSubmit={handleSubmit}
      >
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
            defaultValue={isEditMode ? product.name : ""}
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
            defaultValue={isEditMode ? product.minimum_stock_lvl : ""}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="product-category">Category</label>
          <select
            key={`cat-${categoriesLoading}-${product?.category_id ?? ""}`}
            id="product-category"
            name="category"
            defaultValue={isEditMode ? (product.category_id ?? "") : ""}
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
            key={`sup-${suppliersLoading}-${product?.supplier_id ?? ""}`}
            id="product-supplier"
            name="supplier"
            defaultValue={isEditMode ? (product.supplier_id ?? "") : ""}
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
            defaultValue={isEditMode ? product.cost_price : ""}
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
            defaultValue={isEditMode ? product.selling_price : ""}
            required
          />
        </div>

        <div className="form-group full-width">
          <label htmlFor="product-description">Description</label>
          <textarea
            id="product-description"
            name="description"
            placeholder="Enter product description"
            maxLength="150"
            rows="3"
            defaultValue={initialDescription}
          />
        </div>

        <div className="dialog-actions">
          <Button type="button" variant="secondary" onClick={handleClose}>
            Cancel
          </Button>

          <Button type="submit" disabled={submitting}>
            {submitting
              ? isEditMode
                ? "Saving..."
                : "Adding..."
              : isEditMode
                ? "Save Changes"
                : "Add Product"}
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
