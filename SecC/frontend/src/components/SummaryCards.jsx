import React from 'react';

function formatNumber(value) {
    if (value === null || value === undefined) return 'N/A';
    return typeof value === 'number' ? value.toLocaleString() : value;
}

export default function SummaryCards({ summary }) {
    const cards = [
        { label: 'Total Facilities', value: summary?.total },
        { label: 'Average Mortality', value: summary?.avgMortality },
        { label: 'Min Mortality', value: summary?.minMortality },
        { label: 'Max Mortality', value: summary?.maxMortality },
    ];

    return (
        <div className="card-grid">
            {cards.map((card) => (
                <div className="metric-card" key={card.label}>
                    <div className="metric-label">{card.label}</div>
                    <div className="metric-value">{formatNumber(card.value)}</div>
                </div>
            ))}
        </div>
    );
}
