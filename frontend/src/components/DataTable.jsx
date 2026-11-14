import "../styles/DataTable.css";

export default function DataTable({ columns = [], data = [] }) {
  const getColumnClass = (column) => {
    if (column.align === "right") return "text-right mono-text";
    if (column.align === "center") return "text-center";
    if (column.mono) return "mono-text";
    return "";
  };

  return (
    <table className="data-table">
      <thead>
        <tr>
          {columns.map((column) => (
            <th key={column.key} className={getColumnClass(column)}>
              {column.label}
            </th>
          ))}
        </tr>
      </thead>

      <tbody>
        {data.length === 0 ? (
          <tr>
            <td colSpan={columns.length}>No data available</td>
          </tr>
        ) : (
          data.map((row, index) => (
            <tr key={row.id ?? index}>
              {columns.map((column) => (
                <td key={column.key} className={getColumnClass(column)}>
                  {column.render
                    ? column.render(row[column.key], row)
                    : row[column.key]}
                </td>
              ))}
            </tr>
          ))
        )}
      </tbody>
    </table>
  );
}
