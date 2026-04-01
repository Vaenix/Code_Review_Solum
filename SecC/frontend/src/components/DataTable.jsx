import React from 'react';

export default function DataTable({
    data,
    page,
    pageSize,
    total,
    onPageChange
}) {
    const totalPages = Math.max(1, Math.ceil((total || 0) / pageSize));

    return (
        <div className="panel">
            <div className="panel-header-row">
                <h3>Facility Table</h3>
                <div className="pagination">
                    <button disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
                        Prev
                    </button>
                    <span>Page {page} / {totalPages}</span>
                    <button disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>
                        Next
                    </button>
                </div>
            </div>

            <div className="table-wrap">
                <table className="simple-table">
                    <thead>
                        <tr>
                            <th>Facility</th>
                            <th>State</th>
                            <th>ZIP</th>
                            <th>Year</th>
                            <th>Month</th>
                            <th>Mortality</th>
                            <th>CCN</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data?.length ? (
                            data.map((row, index) => (
                                <tr key={`${row.ccn || row.facilityName}-${index}`}>
                                    <td>{row.facilityName}</td>
                                    <td>{row.state}</td>
                                    <td>{row.zipCode}</td>
                                    <td>{row.year ?? 'N/A'}</td>
                                    <td>{row.month ?? 'N/A'}</td>
                                    <td>{row.mortalityRate ?? 'N/A'}</td>
                                    <td>{row.ccn ?? 'N/A'}</td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="7">No data found.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div className="table-footer">
                Total rows: {total ?? 0}
            </div>
        </div>
    );
}
