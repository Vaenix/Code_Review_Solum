import React, { useEffect, useState } from 'react';
import {
    BarChart, Bar, CartesianGrid, Cell,
    ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts';
import { fetchAnalysis, fetchFilters } from '../api';
import FilterBar from '../components/FilterBar.jsx';

const initialFilters = {
    year: '',
    month: '',
    state: '',
    zip: '',
    facility_name: '',
};

const emptyAnalysis = {
    reportPeriod: null,
    trendMode: 'single_period',
    monthlyTrend: [],
    byState: [],
    byZip: [],
    distribution: [],
    facilityRanking: [],
    summary: {
        totalFacilities: 0,
        facilitiesWithMortality: 0,
    },
};

export default function AnalysisPage() {
    const [filters, setFilters] = useState(initialFilters);
    const [filterOptions, setFilterOptions] = useState({ years: [], months: [], states: [] });
    const [analysis, setAnalysis] = useState(emptyAnalysis);
    const [loading, setLoading] = useState(true);
    const [filterError, setFilterError] = useState('');
    const [dataError, setDataError] = useState('');

    useEffect(() => {
        let cancelled = false;

        fetchFilters()
            .then((response) => {
                if (cancelled) {
                    return;
                }

                setFilterOptions({
                    years: response?.years || [],
                    months: response?.months || [],
                    states: response?.states || [],
                });
                setFilterError('');
            })
            .catch((error) => {
                if (!cancelled) {
                    setFilterError(error.message || 'Failed to load filter options.');
                }
            });

        return () => {
            cancelled = true;
        };
    }, []);

    useEffect(() => {
        let cancelled = false;

        setLoading(true);
        setDataError('');

        fetchAnalysis(filters)
            .then((response) => {
                if (!cancelled) {
                    setAnalysis({
                        ...emptyAnalysis,
                        ...response,
                        summary: {
                            ...emptyAnalysis.summary,
                            ...(response?.summary || {}),
                        },
                    });
                }
            })
            .catch((error) => {
                if (!cancelled) {
                    setAnalysis(emptyAnalysis);
                    setDataError(error.message || 'Failed to load analysis data.');
                }
            })
            .finally(() => {
                if (!cancelled) {
                    setLoading(false);
                }
            });

        return () => {
            cancelled = true;
        };
    }, [filters]);

    function handleFilterChange(key, value) {
        setFilters((prev) => ({ ...prev, [key]: value }));
    }

    function handleReset() {
        setFilters(initialFilters);
    }

    const showEmptyState = !loading && !dataError && analysis.summary.totalFacilities === 0;

    return (
        <div className="page-stack">
            <FilterBar
                filters={filters}
                filterOptions={filterOptions}
                onChange={handleFilterChange}
                onReset={handleReset}
            />

            {filterError && <div className="error-box">{filterError}</div>}
            {dataError && <div className="error-box">{dataError}</div>}
            {loading && <div className="panel">Loading...</div>}

            {!loading && (
                <>
                    <div className="chart-grid">
                        <div className="panel chart-panel">
                            <h3>Report Period Overview</h3>
                            <p className="subtle-text">
                                This dataset represents a single published reporting period rather than true monthly observations.
                            </p>
                            <div className="stat-list">
                                <div><strong>Period:</strong> {analysis.reportPeriod || 'Not provided'}</div>
                                <div><strong>Filtered facilities:</strong> {analysis.summary.totalFacilities}</div>
                                <div><strong>Facilities with mortality data:</strong> {analysis.summary.facilitiesWithMortality}</div>
                            </div>
                        </div>

                        <div className="panel chart-panel">
                            <h3>Highest Average Mortality by State</h3>
                            <ResponsiveContainer width="100%" height={280}>
                                <BarChart data={(analysis.byState || []).slice(0, 15)}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="state" />
                                    <YAxis />
                                    <Tooltip />
                                    <Bar dataKey="avgMortality" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>

                        <div className="panel chart-panel">
                            <h3>Highest-Volume ZIP Areas</h3>
                            <ResponsiveContainer width="100%" height={280}>
                                <BarChart data={(analysis.byZip || []).slice(0, 15)}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="zipCode" />
                                    <YAxis />
                                    <Tooltip />
                                    <Bar dataKey="avgMortality" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>

                        <div className="panel chart-panel">
                            <h3>Mortality Distribution</h3>
                            <ResponsiveContainer width="100%" height={280}>
                                <BarChart data={analysis.distribution || []}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="range" hide />
                                    <YAxis />
                                    <Tooltip />
                                    <Bar dataKey="count">
                                        {(analysis.distribution || []).map((entry, index) => (
                                            <Cell key={`cell-${index}`} />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    <div className="panel">
                        <h3>Facility Ranking Table</h3>
                        <p className="subtle-text">
                            Ranked by facility mortality rate within the current filtered report period.
                        </p>
                        <div className="table-wrap">
                            <table className="simple-table">
                                <thead>
                                    <tr>
                                        <th>Facility</th>
                                        <th>State</th>
                                        <th>ZIP</th>
                                        <th>Mortality</th>
                                        <th>CCN</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {(analysis.facilityRanking || []).length ? (
                                        analysis.facilityRanking.map((row, index) => (
                                            <tr key={`${row.ccn || row.facilityName}-${index}`}>
                                                <td>{row.facilityName}</td>
                                                <td>{row.state}</td>
                                                <td>{row.zipCode}</td>
                                                <td>{row.mortalityRate}</td>
                                                <td>{row.ccn}</td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="5">No analysis data found.</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {showEmptyState && (
                        <div className="info-box">
                            No analysis data matched the current filters. Clear or relax the filters to see state, ZIP, and distribution insights.
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
