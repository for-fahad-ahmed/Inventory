import "../styles/Pagination.css";
import Button from "./Button.jsx";

export default function Pagination({
  page = 1,
  limit = 10,
  total = 0,
  currentCount = 0,
  hasMore,
  onPageChange,
  onLimitChange,
  limitOptions = [10, 25, 50],
  itemLabel = "items",
  disabled = false,
}) {
  const safeLimit = Math.max(1, Number(limit) || 10);
  const effectiveTotal = Math.max(Number(total) || 0, currentCount);
  const totalPages = Math.max(1, Math.ceil(effectiveTotal / safeLimit));
  const currentPage = Math.min(Math.max(1, Number(page) || 1), totalPages);

  const skip = (currentPage - 1) * safeLimit;
  const startItem = effectiveTotal === 0 ? 0 : skip + 1;
  const endItem =
    effectiveTotal === 0
      ? 0
      : Math.min(
          skip + (currentCount > 0 ? currentCount : safeLimit),
          effectiveTotal,
        );

  const canGoPrev = currentPage > 1 && !disabled;
  const canGoNext =
    (typeof hasMore === "boolean" ? hasMore : currentPage < totalPages) &&
    !disabled;

  const handlePrev = () => {
    if (canGoPrev && onPageChange) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (canGoNext && onPageChange) {
      onPageChange(currentPage + 1);
    }
  };

  const handleLimitSelect = (e) => {
    if (onLimitChange) {
      onLimitChange(Number(e.target.value));
    }
  };

  return (
    <div className="pagination" role="navigation" aria-label="Table pagination">
      <div className="pagination-meta">
        <span className="pagination-info">
          {effectiveTotal === 0 ? (
            `Showing 0 ${itemLabel}`
          ) : (
            <>
              Showing <strong>{startItem}</strong>–<strong>{endItem}</strong> of{" "}
              <strong>{effectiveTotal}</strong> {itemLabel}
            </>
          )}
        </span>

        {onLimitChange && (
          <div className="pagination-limit">
            <label htmlFor="pagination-limit-select">Rows per page</label>
            <select
              id="pagination-limit-select"
              value={safeLimit}
              onChange={handleLimitSelect}
              disabled={disabled}
            >
              {limitOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="pagination-controls">
        <Button
          type="button"
          variant="secondary"
          className="btn pagination-btn"
          onClick={handlePrev}
          disabled={!canGoPrev}
        >
          Previous
        </Button>

        <span className="pagination-page" aria-live="polite">
          Page <strong>{currentPage}</strong> of <strong>{totalPages}</strong>
        </span>

        <Button
          type="button"
          variant="secondary"
          className="btn pagination-btn"
          onClick={handleNext}
          disabled={!canGoNext}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
