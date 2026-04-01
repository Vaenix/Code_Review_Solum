import React, { useEffect, useMemo, useState } from 'react';
import { fetchFilters, fetchSummary, fetchTable } from '../api';
import FilterBar from '../components/FilterBar';
import SummaryCards from '../components/SummaryCards';
import TopList from '../components/TopList';
import DataTable from '../components/DataTable';

const initialFilters = {
    year: '',
    month: '',
    state: '',
    zip: '',
    facility_name: '',
};

const emptySummary = {
    total: 0,
    avgMortality: null,
    minMortality: null,
    maxMortality: null,
    reportPeriod: null,
    top10Highest: [],
    top10Lowest: [],
};

export default function SummaryPage() {
    const [filters, setFilters] = useState(initialFilters);
    const [filterOptions, setFilterOptions] = useState({ years: [], months: [], states: [] });
    const [summary, setSummary] = useState(emptySummary);
    const [tableData, setTableData] = useState({ data: [], page: 1, pageSize: 20, total: 0 });
    const [loading, setLoading] = useState(true);
    const [filterError, setFilterError] = useState('');
    const [dataError, setDataError] = useState('');

    const tableParams = useMemo(() => ({
        ...filters,
        page: tableData.page,
        page_size: tableData.pageSize,
    }), [filters, tableData.page, tableData.pageSize]);

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

        Promise.all([
            fetchSummary(filters),
            fetchTable(tableParams),
        ])
            .then(([summaryRes, tableRes]) => {
                if (cancelled) {
                    return;
                }

                setSummary(summaryRes);
                setTableData({
                    data: tableRes.data || [],
                    total: tableRes.total || 0,
                    page: tableRes.page || 1,
                    pageSize: tableRes.pageSize || 20,
                });
            })
            .catch((error) => {
                if (cancelled) {
                    return;
                }

                setSummary(emptySummary);
                setTableData((prev) => ({
                    ...prev,
                    data: [],
                    total: 0,
                }));
                setDataError(error.message || 'Failed to load summary data.');
            })
            .finally(() => {
                if (!cancelled) {
                    setLoading(false);
                }
            });

        return () => {
            cancelled = true;
        };
    }, [filters, tableParams]);

    function handleFilterChange(key, value) {
        setTableData((prev) => ({ ...prev, page: 1 }));
        setFilters((prev) => ({ ...prev, [key]: value }));
    }

    function handleReset() {
        setTableData((prev) => ({ ...prev, page: 1 }));
        setFilters(initialFilters);
    }

    function handlePageChange(newPage) {
        setTableData((prev) => ({ ...prev, page: newPage }));
    }

    const showEmptyState = !loading && !dataError && summary.total === 0;

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
                    {summary.reportPeriod && (
                        <div className="panel">
                            <strong>Report period:</strong> {summary.reportPeriod}
                        </div>
                    )}

                    <SummaryCards summary={summary} />

                    <div className="two-col">
                        <TopList title="Top 10 Highest Mortality Facilities" items={summary.top10Highest} />
                        <TopList title="Top 10 Lowest Mortality Facilities" items={summary.top10Lowest} />
                    </div>

                    <DataTable
                        data={tableData.data}
                        page={tableData.page}
                        pageSize={tableData.pageSize}
                        total={tableData.total}
                        onPageChange={handlePageChange}
                    />

                    {showEmptyState && (
                        <div className="info-box">
                            No facilities matched the current filters. Adjust the filters to see summary metrics and rankings.
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
