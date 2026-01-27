// Enhanced Admin Dashboard JavaScript - FULLY FIXED VERSION
let currentPage = 1;
let pageSize = 20;
let totalRecords = 0;
let currentDateRange = { start: null, end: null, type: 'today' };
let charts = {};
let allVisitors = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log("🚀 Dashboard initializing...");
    
    // ADD EVENT LISTENERS FOR CHART DROPDOWNS
    setTimeout(() => {
        document.querySelectorAll('.chart-select').forEach(select => {
            select.addEventListener('change', updateCharts);
        });
        console.log("✅ Chart dropdown listeners added");
    }, 100);
    
    // Check if we're on the enhanced dashboard
    const isEnhancedDashboard = document.querySelector('.charts-section') !== null;
    console.log("Enhanced Dashboard:", isEnhancedDashboard);
    
    // Set default dates for enhanced dashboard
    if (isEnhancedDashboard) {
        const today = new Date();
        const todayStr = today.toISOString().split('T')[0];
        
        const startDateEl = document.getElementById('startDate');
        const endDateEl = document.getElementById('endDate');
        
        if (startDateEl && endDateEl) {
            startDateEl.value = todayStr;
            endDateEl.value = todayStr;
            
            // Initialize currentDateRange with actual dates
            currentDateRange = { 
                start: todayStr, 
                end: todayStr, 
                type: 'today' 
            };
            console.log("✅ Date range set:", currentDateRange);
        }
    }
    
    // Check login and load data
    checkLoginStatus().then(isLoggedIn => {
        if (isLoggedIn) {
            if (isEnhancedDashboard) {
                // Initialize charts first
                console.log("📊 Initializing charts...");
                initializeCharts();
                
                // Then load analytics with actual dates
                setTimeout(() => {
                    console.log("📈 Loading analytics data...");
                    loadAnalytics();
                }, 200);
                
                // Auto refresh every 30 seconds
                setInterval(() => {
                    if (!document.hidden) {
                        console.log("🔄 Auto-refreshing analytics...");
                        loadAnalytics();
                    }
                }, 30000);
            } else {
                // For basic dashboard
                console.log("📋 Loading basic dashboard...");
                loadVisitors();
                
                // Auto refresh every 30 seconds
                setInterval(() => {
                    if (!document.hidden) {
                        loadVisitors();
                    }
                }, 30000);
            }
        }
    });
});

// Check login status
async function checkLoginStatus() {
    try {
        const res = await fetch('/admin/check_session');
        const data = await res.json();
        
        if (!data.logged_in && !window.location.pathname.includes('/login')) {
            console.warn("❌ Not logged in, redirecting...");
            window.location.href = '/admin/login';
            return false;
        }
        console.log("✅ Login status verified");
        return true;
    } catch (error) {
        console.error('❌ Session check error:', error);
        if (!window.location.pathname.includes('/login')) {
            window.location.href = '/admin/login';
        }
        return false;
    }
}

// ==================== ENHANCED DASHBOARD FUNCTIONS ====================

// Date range selection
function selectDateRange(type) {
    const today = new Date();
    let startDate, endDate;
    
    console.log("📅 Selecting date range:", type);
    
    // Update active button
    document.querySelectorAll('.quick-dates button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    switch(type) {
        case 'today':
            startDate = endDate = today.toISOString().split('T')[0];
            break;
        case 'yesterday':
            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);
            startDate = endDate = yesterday.toISOString().split('T')[0];
            break;
        case 'week':
            const weekAgo = new Date(today);
            weekAgo.setDate(weekAgo.getDate() - 7);
            startDate = weekAgo.toISOString().split('T')[0];
            endDate = today.toISOString().split('T')[0];
            break;
        case 'month':
            const monthAgo = new Date(today);
            monthAgo.setDate(monthAgo.getDate() - 30);
            startDate = monthAgo.toISOString().split('T')[0];
            endDate = today.toISOString().split('T')[0];
            break;
        default:
            startDate = endDate = today.toISOString().split('T')[0];
    }
    
    const startDateEl = document.getElementById('startDate');
    const endDateEl = document.getElementById('endDate');
    
    if (startDateEl && endDateEl) {
        startDateEl.value = startDate;
        endDateEl.value = endDate;
    }
    
    currentDateRange = { start: startDate, end: endDate, type };
    console.log("✅ Date range updated:", currentDateRange);
    loadAnalytics();
}

// Apply custom date range
function applyCustomDateRange() {
    const startDateEl = document.getElementById('startDate');
    const endDateEl = document.getElementById('endDate');
    
    if (!startDateEl || !endDateEl) {
        console.error("❌ Date input elements not found");
        return;
    }
    
    let startDate = startDateEl.value;
    let endDate = endDateEl.value;
    
    // If dates are empty, set to today
    if (!startDate) {
        const today = new Date().toISOString().split('T')[0];
        startDate = today;
        startDateEl.value = today;
    }
    
    if (!endDate) {
        const today = new Date().toISOString().split('T')[0];
        endDate = today;
        endDateEl.value = today;
    }
    
    if (new Date(startDate) > new Date(endDate)) {
        alert('Start date must be before end date');
        return;
    }
    
    // Remove active class from quick date buttons
    document.querySelectorAll('.quick-dates button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    currentDateRange = { start: startDate, end: endDate, type: 'custom' };
    console.log("✅ Custom date range applied:", currentDateRange);
    loadAnalytics();
}

// Load analytics data - FIXED VERSION
async function loadAnalytics() {
    try {
        console.log("📊 Loading analytics...");
        
        // Ensure we have valid dates
        let startDate = currentDateRange.start;
        let endDate = currentDateRange.end;
        
        // If dates are null or invalid, use today
        if (!startDate || startDate === 'null') {
            startDate = new Date().toISOString().split('T')[0];
            currentDateRange.start = startDate;
        }
        
        if (!endDate || endDate === 'null') {
            endDate = new Date().toISOString().split('T')[0];
            currentDateRange.end = endDate;
        }
        
        const params = new URLSearchParams({
            start_date: startDate,
            end_date: endDate
        });
        
        console.log("📡 Fetching analytics with params:", params.toString());
        
        const response = await fetch(`/admin/analytics/advanced?${params}`);
        
        if (response.status === 401) {
            console.warn("❌ Unauthorized, redirecting to login");
            window.location.href = '/admin/login';
            return;
        }
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("✅ Analytics data received:", data);
        
        // Update statistics
        updateStatistics(data);
        
        // Update charts with data
        updateChartData(data);
        
        // Load visitors
        loadVisitors();
        
    } catch (error) {
        console.error('❌ Error loading analytics:', error);
        showNotification('Error loading analytics data: ' + error.message, 'error');
    }
}

// Update statistics - FIXED VERSION
function updateStatistics(data) {
    console.log("📈 Updating statistics...");
    
    const stats = data.stats || {};
    const levelData = data.levelData || { values: [0, 0, 0] };
    
    const elements = {
        totalVisitors: document.getElementById('totalVisitors'),
        currentVisitors: document.getElementById('currentVisitors'),
        avgDuration: document.getElementById('avgDuration'),
        jcCount: document.getElementById('jcCount'),
        ugCount: document.getElementById('ugCount'),
        pgCount: document.getElementById('pgCount')
    };
    
    // Safely update each element
    if (elements.totalVisitors) elements.totalVisitors.textContent = stats.total || 0;
    if (elements.currentVisitors) elements.currentVisitors.textContent = stats.active || 0;
    if (elements.avgDuration) elements.avgDuration.textContent = stats.avgDuration || 0;
    
    // Level counts
    if (levelData.labels && levelData.values) {
        const jcIndex = levelData.labels.indexOf('JC');
        const ugIndex = levelData.labels.indexOf('UG');
        const pgIndex = levelData.labels.indexOf('PG');
        
        if (elements.jcCount) elements.jcCount.textContent = jcIndex !== -1 ? levelData.values[jcIndex] : 0;
        if (elements.ugCount) elements.ugCount.textContent = ugIndex !== -1 ? levelData.values[ugIndex] : 0;
        if (elements.pgCount) elements.pgCount.textContent = pgIndex !== -1 ? levelData.values[pgIndex] : 0;
    }
    
    console.log("✅ Statistics updated");
}

// Initialize charts - FIXED VERSION WITH ERROR HANDLING
function initializeCharts() {
    console.log("📊 Initializing charts...");
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error("❌ Chart.js is not loaded!");
        showNotification("Chart library not loaded. Please refresh the page.", "error");
        return;
    }
    
    const chartElements = {
        level: document.getElementById('levelChart'),
        trend: document.getElementById('trendChart'),
        course: document.getElementById('courseChart'),
        purpose: document.getElementById('purposeChart'),
        hours: document.getElementById('peakHoursChart'),
        duration: document.getElementById('durationChart')
    };
    
    // Check if we're on the enhanced dashboard
    if (!chartElements.level) {
        console.log("ℹ️ Not on enhanced dashboard - skipping chart initialization");
        return;
    }
    
    try {
        // Level Distribution Chart
        if (chartElements.level) {
            const levelCtx = chartElements.level.getContext('2d');
            charts.level = new Chart(levelCtx, {
                type: 'pie',
                data: {
                    labels: ['JC', 'UG', 'PG'],
                    datasets: [{
                        data: [0, 0, 0],
                        backgroundColor: ['#f59e0b', '#10b981', '#8b5cf6'],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { 
                            position: 'bottom',
                            labels: { padding: 15, font: { size: 12 } }
                        }
                    }
                }
            });
            console.log("✅ Level chart created");
        }
        
        // Daily Trend Chart
        if (chartElements.trend) {
            const trendCtx = chartElements.trend.getContext('2d');
            charts.trend = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Daily Visitors',
                        data: [],
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { 
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        }
                    },
                    plugins: {
                        legend: { display: true, position: 'top' }
                    }
                }
            });
            console.log("✅ Trend chart created");
        }
        
        // Course Distribution Chart - FIXED FOR HORIZONTAL/VERTICAL
        if (chartElements.course) {
            const courseCtx = chartElements.course.getContext('2d');
            charts.course = new Chart(courseCtx, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Visitors by Course',
                        data: [],
                        backgroundColor: 'rgba(99, 102, 241, 0.8)',
                        borderColor: '#6366f1',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'x', // Default vertical bars
                    scales: {
                        x: {
                            beginAtZero: true
                        },
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            console.log("✅ Course chart created");
        }
        
        // Purpose Distribution Chart
        if (chartElements.purpose) {
            const purposeCtx = chartElements.purpose.getContext('2d');
            charts.purpose = new Chart(purposeCtx, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            '#6366f1', '#8b5cf6', '#ec4899', '#f59e0b',
                            '#10b981', '#3b82f6', '#ef4444', '#14b8a6'
                        ],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { 
                            position: 'bottom',
                            labels: { padding: 10, font: { size: 11 } }
                        }
                    }
                }
            });
            console.log("✅ Purpose chart created");
        }
        
        // Peak Hours Chart
        if (chartElements.hours) {
            const hoursCtx = chartElements.hours.getContext('2d');
            charts.hours = new Chart(hoursCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Visitors per Hour',
                        data: [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { 
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        }
                    }
                }
            });
            console.log("✅ Peak hours chart created");
        }
        
        // Duration Chart
        if (chartElements.duration) {
            const durationCtx = chartElements.duration.getContext('2d');
            charts.duration = new Chart(durationCtx, {
                type: 'bar',
                data: {
                    labels: ['<30 min', '30-60 min', '1-2 hrs', '2-4 hrs', '>4 hrs'],
                    datasets: [{
                        label: 'Visitors by Duration',
                        data: [0, 0, 0, 0, 0],
                        backgroundColor: 'rgba(236, 72, 153, 0.8)',
                        borderColor: '#ec4899',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { 
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        }
                    }
                }
            });
            console.log("✅ Duration chart created");
        }
        
        console.log("✅ All charts initialized successfully");
        
    } catch (error) {
        console.error("❌ Error initializing charts:", error);
        showNotification("Error creating charts: " + error.message, "error");
    }
}

// Update charts with new data - FIXED VERSION
function updateChartData(data) {
    console.log("📊 Updating charts with data...");
    
    if (!charts.level) {
        console.warn("⚠️ Charts not initialized");
        return;
    }
    
    try {
        // Level Chart
        if (charts.level && data.levelData) {
            charts.level.data.labels = data.levelData.labels || [];
            charts.level.data.datasets[0].data = data.levelData.values || [];
            charts.level.update('none'); // 'none' for faster updates
            console.log("✅ Level chart updated");
        }
        
        // Daily Trend
        if (charts.trend && data.dailyTrend) {
            charts.trend.data.labels = data.dailyTrend.labels || [];
            charts.trend.data.datasets[0].data = data.dailyTrend.values || [];
            charts.trend.update('none');
            console.log("✅ Trend chart updated");
        }
        
        // Course Distribution
        if (charts.course && data.courseData) {
            charts.course.data.labels = data.courseData.labels || [];
            charts.course.data.datasets[0].data = data.courseData.values || [];
            charts.course.update('none');
            console.log("✅ Course chart updated");
        }
        
        // Purpose Distribution
        if (charts.purpose && data.purposeData) {
            charts.purpose.data.labels = data.purposeData.labels || [];
            charts.purpose.data.datasets[0].data = data.purposeData.values || [];
            charts.purpose.update('none');
            console.log("✅ Purpose chart updated");
        }
        
        // Peak Hours
        if (charts.hours && data.peakHours) {
            charts.hours.data.labels = data.peakHours.labels || [];
            charts.hours.data.datasets[0].data = data.peakHours.values || [];
            charts.hours.update('none');
            console.log("✅ Peak hours chart updated");
        }
        
        // Duration Analysis - FIXED VERSION
        if (charts.duration && data.visitors) {
            // Calculate duration distribution
            const durations = [0, 0, 0, 0, 0]; // <30, 30-60, 1-2, 2-4, >4 hours
            
            if (Array.isArray(data.visitors)) {
                data.visitors.forEach(v => {
                    if (v.entry_time && v.exit_time) {
                        try {
                            const entry = new Date(`2000-01-01 ${v.entry_time}`);
                            const exit = new Date(`2000-01-01 ${v.exit_time}`);
                            const minutes = (exit - entry) / 60000;
                            
                            if (minutes < 30) durations[0]++;
                            else if (minutes < 60) durations[1]++;
                            else if (minutes < 120) durations[2]++;
                            else if (minutes < 240) durations[3]++;
                            else durations[4]++;
                        } catch (e) {
                            console.warn("⚠️ Error calculating duration:", e);
                        }
                    }
                });
            }
            
            // Update the chart
            charts.duration.data.datasets[0].data = durations;
            
            // Make sure labels are set correctly
            const durationLabels = ['<30 min', '30-60 min', '1-2 hrs', '2-4 hrs', '>4 hrs'];
            if (charts.duration.data.labels.length === 0) {
                charts.duration.data.labels = durationLabels;
            }
            
            charts.duration.update();
            console.log("✅ Duration chart updated with data:", durations);
        }
        
        console.log("✅ All charts updated successfully");
        
    } catch (error) {
        console.error("❌ Error updating charts:", error);
    }
}

// Change chart type - FIXED VERSION
function updateCharts() {
    console.log("🔄 Updating chart types...");
    
    try {
        // Level Chart
        if (charts.level) {
            const levelType = document.getElementById('chartLevelType');
            if (levelType) {
                charts.level.config.type = levelType.value;
                charts.level.update();
                console.log("✅ Level chart type changed to:", levelType.value);
            }
        }
        
        // Trend Chart
        if (charts.trend) {
            const trendType = document.getElementById('chartTrendType');
            if (trendType) {
                charts.trend.config.type = trendType.value;
                charts.trend.update();
                console.log("✅ Trend chart type changed to:", trendType.value);
            }
        }
        
        // Course Chart - FIXED FOR HORIZONTAL/VERTICAL
        if (charts.course) {
            const courseType = document.getElementById('chartCourseType');
            if (courseType) {
                const type = courseType.value;
                
                // Store current data
                const currentData = {
                    labels: charts.course.data.labels || [],
                    datasets: charts.course.data.datasets.map(dataset => ({
                        ...dataset
                    }))
                };
                
                // Destroy and recreate the chart with new configuration
                charts.course.destroy();
                
                // For Chart.js v4.x: Use 'bar' type with different indexAxis
                if (type === 'horizontalBar') {
                    charts.course = new Chart(document.getElementById('courseChart').getContext('2d'), {
                        type: 'bar',
                        data: currentData,
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            indexAxis: 'y', // This makes it horizontal
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: 'Courses'
                                    },
                                    grid: {
                                        display: true
                                    }
                                },
                                x: {
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: 'Number of Visitors'
                                    },
                                    ticks: {
                                        callback: function(value) {
                                            if (Math.floor(value) === value) {
                                                return value;
                                            }
                                        }
                                    }
                                }
                            },
                            plugins: {
                                legend: {
                                    display: false // Hide legend for cleaner horizontal bars
                                }
                            }
                        }
                    });
                } else {
                    // Vertical bars
                    charts.course = new Chart(document.getElementById('courseChart').getContext('2d'), {
                        type: 'bar',
                        data: currentData,
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            indexAxis: 'x', // This is the default for vertical bars
                            scales: {
                                x: {
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: 'Courses'
                                    }
                                },
                                y: {
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: 'Number of Visitors'
                                    },
                                    ticks: {
                                        callback: function(value) {
                                            if (Math.floor(value) === value) {
                                                return value;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    });
                }
                
                console.log("✅ Course chart type changed to:", type);
            }
        }
        
        // Purpose Chart
        if (charts.purpose) {
            const purposeType = document.getElementById('chartPurposeType');
            if (purposeType) {
                charts.purpose.config.type = purposeType.value;
                charts.purpose.update();
                console.log("✅ Purpose chart type changed to:", purposeType.value);
            }
        }
        
        // Peak Hours Chart
        if (charts.hours) {
            const hoursType = document.getElementById('chartHoursType');
            if (hoursType) {
                charts.hours.config.type = hoursType.value;
                charts.hours.update();
                console.log("✅ Peak hours chart type changed to:", hoursType.value);
            }
        }
        
        console.log("✅ All chart types updated");
    } catch (error) {
        console.error("❌ Error updating charts:", error);
    }
}

// ==================== VISITOR TABLE FUNCTIONS ====================

// Load visitors with pagination
async function loadVisitors() {
    try {
        console.log("📋 Loading visitors...");
        
        const table = document.getElementById('visitorTable');
        if (!table) {
            console.warn("⚠️ Visitor table not found");
            return;
        }
        
        // Check if we're on enhanced dashboard
        const isEnhanced = document.querySelector('.charts-section') !== null;
        
        // Show loading
        table.innerHTML = `
            <tr>
                <td colspan="${isEnhanced ? '13' : '11'}" class="loading-row">
                    <i class="fas fa-spinner fa-spin"></i>
                    <div>Loading visitor data...</div>
                </td>
            </tr>
        `;
        
        let data = [];
        
        if (isEnhanced) {
            // Enhanced dashboard: use analytics endpoint
            const params = new URLSearchParams();
            params.append('start_date', currentDateRange.start);
            params.append('end_date', currentDateRange.end);
            
            const levelFilter = document.getElementById('levelFilter');
            const statusFilter = document.getElementById('statusFilter');
            
            if (levelFilter && levelFilter.value) params.append('level', levelFilter.value);
            
            const response = await fetch(`/admin/analytics/advanced?${params}`);
            
            if (response.status === 401) {
                window.location.href = "/admin/login";
                return;
            }
            
            const analyticsData = await response.json();
            
            allVisitors = analyticsData.visitors || [];
            
            // Filter by status if needed
            if (statusFilter && statusFilter.value === 'active') {
                allVisitors = allVisitors.filter(v => !v.exit_time);
            } else if (statusFilter && statusFilter.value === 'exited') {
                allVisitors = allVisitors.filter(v => v.exit_time);
            }
            
            totalRecords = allVisitors.length;
            renderTablePage();
            
        } else {
            // Basic dashboard: use simple endpoints
            let url = "/admin/visitors/today";
            
            const params = new URLSearchParams();
            const levelFilter = document.getElementById('levelFilter');
            const dateFilter = document.getElementById('dateFilter');
            
            if (levelFilter && levelFilter.value) {
                params.append('level', levelFilter.value);
            }
            if (dateFilter && dateFilter.value) {
                params.append('date', dateFilter.value);
            }
            
            if (params.toString()) {
                url = "/admin/visitors/filter?" + params.toString();
            }
            
            const res = await fetch(url);
            
            if (res.status === 401) {
                window.location.href = "/admin/login";
                return;
            }
            
            data = await res.json();
            
            if (data.length === 0) {
                table.innerHTML = `
                    <tr>
                        <td colspan="11" class="loading-row">
                            <i class="fas fa-inbox"></i>
                            <div>No visitors found</div>
                        </td>
                    </tr>
                `;
                updateStats(data);
                return;
            }
            
            renderBasicTable(data);
            updateStats(data);
        }
        
        console.log("✅ Visitors loaded successfully");
        
    } catch (error) {
        console.error('❌ Error loading visitors:', error);
        const isEnhanced = document.querySelector('.charts-section') !== null;
        const table = document.getElementById('visitorTable');
        if (table) {
            table.innerHTML = `
                <tr>
                    <td colspan="${isEnhanced ? '13' : '11'}" class="loading-row" style="color: #ef4444;">
                        <i class="fas fa-exclamation-triangle"></i>
                        <div>Error loading data. Please try again.</div>
                    </td>
                </tr>
            `;
        }
        showNotification('Error loading visitor data', 'error');
    }
}

// Render current page of table (enhanced)
function renderTablePage() {
    console.log("📄 Rendering table page", currentPage);
    
    const table = document.getElementById('visitorTable');
    if (!table) return;
    
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = Math.min(startIndex + pageSize, totalRecords);
    const pageVisitors = allVisitors.slice(startIndex, endIndex);
    
    if (pageVisitors.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="13" class="loading-row">
                    <i class="fas fa-inbox"></i>
                    <div>No visitors found</div>
                </td>
            </tr>
        `;
        return;
    }
    
    let tableHTML = '';
    
    pageVisitors.forEach(v => {
        let courseDisplay = v.course;
        let yearDisplay = v.year || "-";
        
        if (v.level === "JC") {
            courseDisplay = v.jc_stream || "Junior College";
            yearDisplay = v.jc_year || "-";
        }
        
        // Calculate duration
        let duration = '-';
        if (v.entry_time && v.exit_time) {
            try {
                const entry = new Date(`2000-01-01 ${v.entry_time}`);
                const exit = new Date(`2000-01-01 ${v.exit_time}`);
                const diffMs = exit - entry;
                const minutes = Math.floor(diffMs / 60000);
                duration = `${minutes}m`;
            } catch (e) {
                duration = '-';
            }
        }
        
        tableHTML += `
            <tr>
                <td class="checkbox-cell">
                    <input type="checkbox" class="row-checkbox" value="${v.id}">
                </td>
                <td><strong>${v.name}</strong></td>
                <td><code class="roll-no">${v.roll_no}</code></td>
                <td>${v.level}</td>
                <td>${courseDisplay}</td>
                <td>${yearDisplay}</td>
                <td>${v.purpose}</td>
                <td>${v.entry_time || "-"}</td>
                <td>${v.exit_time || "-"}</td>
                <td>${v.visit_date}</td>
                <td>
                    <span class="status-badge ${v.exit_time ? 'exited' : 'active'}">
                        <i class="fas ${v.exit_time ? 'fa-door-closed' : 'fa-door-open'}"></i>
                        ${v.exit_time ? 'Exited' : 'Active'}
                    </span>
                </td>
                <td>${duration}</td>
                <td>
                    ${!v.exit_time ? `
                        <button class="btn-exit" onclick="markExit(${v.id})">
                            <i class="fas fa-sign-out-alt"></i> Exit
                        </button>
                    ` : ''}
                    <button class="btn btn-secondary view-details-btn" onclick="viewDetails(${v.id})" style="margin-left: 5px; padding: 6px 10px; font-size: 12px;">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    table.innerHTML = tableHTML;
    
    // Update pagination
    const recordCountEl = document.getElementById('recordCount');
    const currentPageEl = document.getElementById('currentPage');
    const totalPagesEl = document.getElementById('totalPages');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (recordCountEl) recordCountEl.textContent = totalRecords;
    if (currentPageEl) currentPageEl.textContent = currentPage;
    if (totalPagesEl) totalPagesEl.textContent = Math.ceil(totalRecords / pageSize) || 1;
    
    if (prevBtn) prevBtn.disabled = currentPage === 1;
    if (nextBtn) nextBtn.disabled = currentPage * pageSize >= totalRecords;
    
    // Update select all checkbox
    const selectAll = document.getElementById('selectAll');
    if (selectAll) selectAll.checked = false;
    
    console.log("✅ Table page rendered");
}

// Render basic table (non-enhanced dashboard)
function renderBasicTable(data) {
    const table = document.getElementById('visitorTable');
    let tableHTML = '';
    
    data.forEach(v => {
        let courseDisplay = v.course;
        let yearDisplay = v.year || "-";
        
        if (v.level === "JC") {
            courseDisplay = v.jc_stream || "Junior College";
            yearDisplay = v.jc_year || "-";
        }
        
        tableHTML += `
            <tr>
                <td><strong>${v.name}</strong></td>
                <td><code class="roll-no">${v.roll_no}</code></td>
                <td>${v.level}</td>
                <td>${courseDisplay}</td>
                <td>${yearDisplay}</td>
                <td>${v.purpose}</td>
                <td>${v.entry_time || "-"}</td>
                <td>${v.exit_time || "-"}</td>
                <td>${v.visit_date}</td>
                <td>
                    <span class="status-badge ${v.exit_time ? 'exited' : 'active'}">
                        <i class="fas ${v.exit_time ? 'fa-door-closed' : 'fa-door-open'}"></i>
                        ${v.exit_time ? 'Exited' : 'Active'}
                    </span>
                </td>
                <td>
                    ${!v.exit_time ? `
                        <button class="btn-exit" onclick="markExit(${v.id})">
                            <i class="fas fa-sign-out-alt"></i> Exit
                        </button>
                    ` : '<span class="exited-text">Exited</span>'}
                </td>
            </tr>
        `;
    });
    
    table.innerHTML = tableHTML;
}

// ==================== PAGINATION & SELECTION ====================

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        renderTablePage();
    }
}

function nextPage() {
    if (currentPage * pageSize < totalRecords) {
        currentPage++;
        renderTablePage();
    }
}

function toggleSelectAll() {
    const selectAll = document.getElementById('selectAll');
    if (!selectAll) return;
    
    const isChecked = selectAll.checked;
    document.querySelectorAll('.row-checkbox').forEach(cb => {
        cb.checked = isChecked;
    });
}

function selectAllRows() {
    const selectAll = document.getElementById('selectAll');
    if (selectAll) {
        selectAll.checked = true;
        document.querySelectorAll('.row-checkbox').forEach(cb => {
            cb.checked = true;
        });
    }
}

function getSelectedVisitorIds() {
    const selected = [];
    document.querySelectorAll('.row-checkbox:checked').forEach(cb => {
        selected.push(parseInt(cb.value));
    });
    return selected;
}

// ==================== BULK ACTIONS ====================

async function applyBulkAction() {
    const bulkActionSelect = document.getElementById('bulkAction');
    if (!bulkActionSelect) return;
    
    const action = bulkActionSelect.value;
    const visitorIds = getSelectedVisitorIds();
    
    if (visitorIds.length === 0) {
        alert('Please select at least one visitor');
        return;
    }
    
    if (!action) {
        alert('Please select an action');
        return;
    }
    
    if (action === 'delete' && !confirm(`Are you sure you want to delete ${visitorIds.length} visitors? This action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch('/admin/bulk_actions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, visitor_ids: visitorIds })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification(result.message, 'success');
            loadVisitors();
            if (document.querySelector('.charts-section')) {
                loadAnalytics();
            }
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        console.error('Bulk action error:', error);
        showNotification('Error performing bulk action', 'error');
    }
}

// ==================== FILTER FUNCTIONS ====================

function applyFilters() {
    currentPage = 1; // Reset to first page
    loadVisitors();
}

function resetFilters() {
    const levelFilter = document.getElementById('levelFilter');
    const statusFilter = document.getElementById('statusFilter');
    const dateFilter = document.getElementById('dateFilter');
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    
    if (levelFilter) levelFilter.value = '';
    if (statusFilter) statusFilter.value = '';
    if (dateFilter) dateFilter.value = '';
    
    if (startDate && endDate) {
        const today = new Date().toISOString().split('T')[0];
        startDate.value = today;
        endDate.value = today;
        currentDateRange = { start: today, end: today, type: 'today' };
    }
    
    document.querySelectorAll('.quick-dates button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const todayBtn = document.querySelector('.quick-dates button:first-child');
    if (todayBtn) todayBtn.classList.add('active');
    
    currentPage = 1;
    
    if (document.querySelector('.charts-section')) {
        loadAnalytics();
    } else {
        loadVisitors();
    }
}

// ==================== VISITOR ACTIONS ====================

async function markExit(visitorId) {
    if (!confirm('Mark this visitor as exited?')) return;
    
    try {
        const response = await fetch(`/student/exit/${visitorId}`, { method: 'PUT' });
        
        if (response.ok) {
            showNotification('Exit marked successfully!', 'success');
            loadVisitors();
            if (document.querySelector('.charts-section')) {
                loadAnalytics();
            }
        } else {
            const data = await response.json();
            showNotification(data.error || 'Failed to mark exit', 'error');
        }
    } catch (error) {
        console.error('Error marking exit:', error);
        showNotification('Error marking exit', 'error');
    }
}

function viewDetails(visitorId) {
    const visitor = allVisitors.find(v => v.id === visitorId);
    if (!visitor) {
        alert('Visitor not found');
        return;
    }
    
    let courseDisplay = visitor.course;
    let yearDisplay = visitor.year || "-";
    
    if (visitor.level === "JC") {
        courseDisplay = visitor.jc_stream || "Junior College";
        yearDisplay = visitor.jc_year || "-";
    }
    
    const details = `
        <div style="text-align: left;">
            <p><strong>Name:</strong> ${visitor.name}</p>
            <p><strong>Roll No:</strong> ${visitor.roll_no}</p>
            <p><strong>Level:</strong> ${visitor.level}</p>
            <p><strong>Course/Stream:</strong> ${courseDisplay}</p>
            <p><strong>Year:</strong> ${yearDisplay}</p>
            <p><strong>Purpose:</strong> ${visitor.purpose}</p>
            <p><strong>Entry Time:</strong> ${visitor.entry_time || 'N/A'}</p>
            <p><strong>Exit Time:</strong> ${visitor.exit_time || 'Not exited yet'}</p>
            <p><strong>Visit Date:</strong> ${visitor.visit_date}</p>
            <p><strong>Day:</strong> ${visitor.visit_day || 'N/A'}</p>
        </div>
    `;
    
    showModal('Visitor Details', details);
}

// ==================== IMPORT/EXPORT ====================

async function importData() {
    const fileInput = document.getElementById('importFile');
    if (!fileInput) return;
    
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file to import');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const resultDiv = document.getElementById('importResult');
    if (resultDiv) {
        resultDiv.innerHTML = '<div class="import-loading"><i class="fas fa-spinner fa-spin"></i> Importing data...</div>';
    }
    
    try {
        const response = await fetch('/admin/import_data', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && resultDiv) {
            resultDiv.innerHTML = `
                <div class="import-success">
                    <div class="import-success-title">
                        <i class="fas fa-check-circle"></i> ${result.message}
                    </div>
                    ${result.errors && result.errors.length > 0 ? `
                        <div class="import-errors">
                            <strong>Errors (${result.errors.length}):</strong>
                            <ul>
                                ${result.errors.slice(0, 5).map(err => `<li>${err}</li>`).join('')}
                            </ul>
                            ${result.errors.length > 5 ? `<em>... and ${result.errors.length - 5} more errors</em>` : ''}
                        </div>
                    ` : ''}
                </div>
            `;
            
            fileInput.value = '';
            
            if (document.querySelector('.charts-section')) {
                loadAnalytics();
            } else {
                loadVisitors();
            }
            
        } else if (resultDiv) {
            resultDiv.innerHTML = `
                <div class="import-error">
                    <i class="fas fa-exclamation-circle"></i> ${result.error || 'Import failed'}
                </div>
            `;
        }
    } catch (error) {
        console.error('Import error:', error);
        if (resultDiv) {
            resultDiv.innerHTML = `
                <div class="import-error">
                    <i class="fas fa-exclamation-circle"></i> Error importing data
                </div>
            `;
        }
    }
}

function downloadTemplate() {
    const template = `name,roll_no,level,course,year,jc_year,jc_stream,purpose
John Doe,JC001,JC,Junior College,,FYJC,Science,Reading
Jane Smith,UG001,UG,B.COM,First Year,,,Book Issue
Bob Johnson,PG001,PG,M.Sc-IT,First Year,,,Research
Alice Brown,JC002,JC,Junior College,,SYJC,Commerce,Newspaper`;

    const blob = new Blob([template], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'library_import_template.csv';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
    
    showNotification('Template downloaded successfully!', 'success');
}

async function exportData(format) {
    try {
        const params = new URLSearchParams({
            format: format,
            start_date: currentDateRange.start || '',
            end_date: currentDateRange.end || ''
        });
        
        const response = await fetch(`/admin/export_data?${params}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `library_export_${new Date().toISOString().split('T')[0]}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
            
            showNotification(`Data exported successfully as ${format.toUpperCase()}`, 'success');
        } else {
            showNotification('Error exporting data', 'error');
        }
    } catch (error) {
        console.error('Export error:', error);
        showNotification('Error exporting data', 'error');
    }
}

// ==================== UTILITY FUNCTIONS ====================

function updateStats(data) {
    const totalVisitors = data.length;
    const currentVisitors = data.filter(v => !v.exit_time).length;
    const jcCount = data.filter(v => v.level === 'JC').length;
    const ugCount = data.filter(v => v.level === 'UG').length;
    const pgCount = data.filter(v => v.level === 'PG').length;
    
    const elements = {
        totalVisitors: document.getElementById('totalVisitors'),
        currentVisitors: document.getElementById('currentVisitors'),
        jcCount: document.getElementById('jcCount'),
        ugCount: document.getElementById('ugCount'),
        pgCount: document.getElementById('pgCount'),
        recordCount: document.getElementById('recordCount')
    };
    
    if (elements.totalVisitors) elements.totalVisitors.textContent = totalVisitors;
    if (elements.currentVisitors) elements.currentVisitors.textContent = currentVisitors;
    if (elements.jcCount) elements.jcCount.textContent = jcCount;
    if (elements.ugCount) elements.ugCount.textContent = ugCount;
    if (elements.pgCount) elements.pgCount.textContent = pgCount;
    if (elements.recordCount) elements.recordCount.textContent = totalVisitors;
}

function showNotification(message, type = 'info') {
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()"><i class="fas fa-times"></i></button>
    `;
    
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                padding: 1rem 1.25rem;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                display: flex;
                align-items: center;
                gap: 0.75rem;
                z-index: 1000;
                animation: slideInRight 0.3s ease;
                border-left: 4px solid;
                min-width: 300px;
                max-width: 400px;
            }
            .notification-success { border-left-color: #10b981; }
            .notification-error { border-left-color: #ef4444; }
            .notification-info { border-left-color: #6366f1; }
            .notification i { font-size: 1.25rem; }
            .notification-success i { color: #10b981; }
            .notification-error i { color: #ef4444; }
            .notification-info i { color: #6366f1; }
            .notification span { flex: 1; }
            .notification button {
                background: none;
                border: none;
                color: #94a3b8;
                cursor: pointer;
                padding: 0.25rem;
            }
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

function showModal(title, content) {
    const existing = document.getElementById('customModal');
    if (existing) existing.remove();
    
    const modal = document.createElement('div');
    modal.id = 'customModal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="closeModal()"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h3>${title}</h3>
                <button onclick="closeModal()"><i class="fas fa-times"></i></button>
            </div>
            <div class="modal-body">
                ${content}
            </div>
            <div class="modal-footer">
                <button onclick="closeModal()" class="btn btn-primary">Close</button>
            </div>
        </div>
    `;
    
    if (!document.getElementById('modal-styles')) {
        const style = document.createElement('style');
        style.id = 'modal-styles';
        style.textContent = `
            #customModal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 2000;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
            }
            .modal-content {
                background: white;
                border-radius: 16px;
                width: 90%;
                max-width: 500px;
                max-height: 80vh;
                overflow: hidden;
                z-index: 2001;
                animation: modalFadeIn 0.3s ease;
            }
            .modal-header {
                padding: 1.5rem;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .modal-header h3 {
                margin: 0;
                color: #1e293b;
            }
            .modal-header button {
                background: none;
                border: none;
                color: #64748b;
                cursor: pointer;
                font-size: 1.25rem;
            }
            .modal-body {
                padding: 1.5rem;
                max-height: 50vh;
                overflow-y: auto;
            }
            .modal-body p {
                margin: 0.5rem 0;
            }
            .modal-footer {
                padding: 1rem 1.5rem;
                border-top: 1px solid #e2e8f0;
                text-align: right;
            }
            @keyframes modalFadeIn {
                from { opacity: 0; transform: scale(0.9); }
                to { opacity: 1; transform: scale(1); }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(modal);
}

function closeModal() {
    const modal = document.getElementById('customModal');
    if (modal) modal.remove();
}

function logoutUser() {
    if (!confirm('Are you sure you want to logout?')) return;
    
    // Direct redirect to logout endpoint
    window.location.href = '/admin/logout';
    
    // OR with timeout to ensure cookies cleared
    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}


console.log("✅ Admin.js loaded successfully!");
