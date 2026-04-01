import React from 'react';

export default function TopList({ title, items }) {
    return (
        <div className="panel">
            <h3>{title}</h3>
            <div className="list-wrap">
                {items?.length ? (
                    <table className="simple-table">
                        <thead>
                            <tr>
                                <th>Facility</th>
                                <th>State</th>
                                <th>ZIP</th>
                                <th>Mortality</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items.map((item, index) => (
                                <tr key={`${item.ccn || item.facilityName}-${index}`}>
                                    <td>{item.facilityName}</td>
                                    <td>{item.state}</td>
                                    <td>{item.zipCode}</td>
                                    <td>{item.mortalityRate}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p>No data available.</p>
                )}
            </div>
        </div>
    );
}
