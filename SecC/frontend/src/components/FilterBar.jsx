import React from 'react';

export default function FilterBar({
    filters,
    filterOptions,
    onChange,
    onReset
}) {
    const years = filterOptions?.years || [];
    const months = filterOptions?.months || [];
    const states = filterOptions?.states || [];

    return (
        <div className="panel filter-bar">
            <div className="filter-grid">
                <label>
                    <span>Year</span>
                    <select
                        value={filters.year}
                        onChange={(e) => onChange('year', e.target.value)}
                    >
                        <option value="">All</option>
                        {years.map((y) => (
                            <option key={y} value={y}>{y}</option>
                        ))}
                    </select>
                </label>

                <label>
                    <span>Month</span>
                    <select
                        value={filters.month}
                        onChange={(e) => onChange('month', e.target.value)}
                    >
                        <option value="">All</option>
                        {months.map((m) => (
                            <option key={m} value={m}>{m}</option>
                        ))}
                    </select>
                </label>

                <label>
                    <span>State</span>
                    <select
                        value={filters.state}
                        onChange={(e) => onChange('state', e.target.value)}
                    >
                        <option value="">All</option>
                        {states.map((s) => (
                            <option key={s} value={s}>{s}</option>
                        ))}
                    </select>
                </label>

                <label>
                    <span>ZIP Code</span>
                    <input
                        type="text"
                        value={filters.zip}
                        placeholder="e.g. 10001"
                        onChange={(e) => onChange('zip', e.target.value)}
                    />
                </label>

                <label className="filter-wide">
                    <span>Facility Name</span>
                    <input
                        type="text"
                        value={filters.facility_name}
                        placeholder="Search facility"
                        onChange={(e) => onChange('facility_name', e.target.value)}
                    />
                </label>
            </div>

            <div className="filter-actions">
                <button onClick={onReset}>Reset Filters</button>
            </div>
        </div>
    );
}
