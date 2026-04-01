import React from 'react';
import { NavLink, Route, Routes } from 'react-router-dom';
import SummaryPage from './pages/SummaryPage.jsx';
import AnalysisPage from './pages/AnalysisPage.jsx';

export default function App() {
    return (
        <div className="app-shell">
            <header className="app-header">
                <div>
                    <h1>CMS Dialysis Mortality Dashboard</h1>
                    <p>Filter, compare, and analyze facility mortality rates</p>
                </div>
                <nav className="nav-tabs">
                    <NavLink to="/" end className={({ isActive }) => isActive ? 'tab active' : 'tab'}>
                        Summary
                    </NavLink>
                    <NavLink to="/analysis" className={({ isActive }) => isActive ? 'tab active' : 'tab'}>
                        Analysis
                    </NavLink>
                </nav>
            </header>

            <main className="app-main">
                <Routes>
                    <Route path="/" element={<SummaryPage />} />
                    <Route path="/analysis" element={<AnalysisPage />} />
                </Routes>
            </main>
        </div>
    );
}