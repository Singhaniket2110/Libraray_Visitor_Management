// Enhanced Admin Dashboard JavaScript - COMPLETE VERSION WITH TEACHER SUPPORT
let currentPage = 1;
let pageSize = 20;
let totalRecords = 0;
let currentDateRange = { start: null, end: null, type: 'today' };
let charts = {};
let allVisitors = [];

// Teacher variables
let currentTeacherPage = 1;
let teacherPageSize = 20;
let teacherTotalRecords = 0;
let allTeachers = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log("🚀 Dashboard initializing...");
    
    // Set default dates
    const today = new Date().toISOString().split('T')[0];
    const startDateEl = document.getElementById('startDate');
    const endDateEl = document.getElementById('endDate');
    
    if (startDateEl && endDateEl) {
        startDateEl.value = today;
        endDateEl.value = today;
        currentDateRange = { start: today, end: today, type: 'today' };
    }
    
    // ADD EVENT LISTENERS FOR CHART DROPDOWNS
    setTimeout(() => {
        document.querySelectorAll('.chart-select').forEach(select => {
            select.addEventListener('change', updateCharts);
        });
        console.log("✅ Chart dropdown listeners added");
    }, 100);
    
    // Check login and load data
    checkLoginStatus().then(isLoggedIn => {
        if (isLoggedIn) {
            // Initialize charts first
            console.log("📊 Initializing charts...");
            initializeCharts();
            
            // Then load all data
            setTimeout(() => {
                console.log("📈 Loading all data...");
                loadAnalytics();
                loadDailyStats();
                loadLifetimeStats();
                loadTeacherStats();
                loadTeacherVisits();
            }, 200);
            
            // Auto refresh every 30 seconds
            setInterval(() => {
                if (!document.hidden) {
                    console.log("🔄 Auto-refreshing...");
                    loadAnalytics();
                    
                    // Refresh active stats tab
                    if (document.getElementById('dailyStats').classList.contains('active')) {
                        loadDailyStats();
                    } else if (document.getElementById('lifetimeStats').classList.contains('active')) {
                        loadLifetimeStats();
                    } else if (document.getElementById('teacherStats').classList.contains('active')) {
                        loadTeacherStats();
                    }
                    
                    loadVisitors();
                    loadTeacherVisits();
                }
            }, 30000);
        }
    });
});

// ==================== AUTHENTICATION ====================

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

// ==================== STATISTICS TABS ====================

function showStatsTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.stats-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.stats-tab').forEach(button => {
        button.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + 'Stats').classList.add('active');
    
    // Activate selected button
    event.target.classList.add('active');
    
    // Load appropriate data
    if (tabName === 'daily') {
        loadDailyStats();
    } else if (tabName === 'lifetime') {
        loadLifetimeStats();
    } else if (tabName === 'teachers') {
        loadTeacherStats();
    }
}

async function loadDailyStats() {
    try {
        const today = new Date().toISOString().split('T')[0];
        const response = await fetch(`/admin/analytics/advanced?start_date=${today}&end_date=${today}`);
        const data = await response.json();
        
        if (data.stats) {
            document.getElementById('dailyTotalVisitors').textContent = data.stats.total || 0;
            document.getElementById('dailyCurrentVisitors').textContent = data.stats.active || 0;
            document.getElementById('dailyAvgDuration').textContent = data.stats.avgDuration || 0;
        }
        
        if (data.levelData) {
            const jcIndex = data.levelData.labels.indexOf('JC');
            const ugIndex = data.levelData.labels.indexOf('UG');
            const pgIndex = data.levelData.labels.indexOf('PG');
            
            document.getElementById('dailyJcCount').textContent = jcIndex !== -1 ? data.levelData.values[jcIndex] : 0;
            document.getElementById('dailyUgCount').textContent = ugIndex !== -1 ? data.levelData.values[ugIndex] : 0;
            document.getElementById('dailyPgCount').textContent = pgIndex !== -1 ? data.levelData.values[pgIndex] : 0;
        }
        
    } catch (error) {
        console.error('Error loading daily stats:', error);
    }
}

async function loadLifetimeStats() {
    try {
        // Get all visitors
        const response = await fetch('/admin/visitors/all');
        const visitors = await response.json();
        
        // Calculate lifetime stats
        const totalVisitors = visitors.length;
        const jcCount = visitors.filter(v => v.level === 'JC').length;
        const ugCount = visitors.filter(v => v.level === 'UG').length;
        const pgCount = visitors.filter(v => v.level === 'PG').length;
        
        // Get unique dates for days of operation
        const uniqueDates = [...new Set(visitors.map(v => v.visit_date))].filter(date => date);
        const totalDays = uniqueDates.length;
        const avgDaily = totalDays > 0 ? (totalVisitors / totalDays).toFixed(1) : 0;
        
        // Update UI
        document.getElementById('lifetimeTotalVisitors').textContent = totalVisitors;
        document.getElementById('lifetimeJcCount').textContent = jcCount;
        document.getElementById('lifetimeUgCount').textContent = ugCount;
        document.getElementById('lifetimePgCount').textContent = pgCount;
        document.getElementById('totalDays').textContent = totalDays;
        document.getElementById('avgDaily').textContent = avgDaily;
        
    } catch (error) {
        console.error('Error loading lifetime stats:', error);
    }
}

async function loadTeacherStats() {
    try {
        const today = new Date().toISOString().split('T')[0];
        
        // Get all teacher visits
        const allResponse = await fetch('/admin/teachers/all');
        const allTeachers = await allResponse.json();
        
        // Get today's teacher visits
        const todayResponse = await fetch(`/admin/teachers/filter?start_date=${today}&end_date=${today}`);
        const todayTeachers = await todayResponse.json();
        
        // Calculate stats
        const teacherTotalVisits = allTeachers.length;
        const teacherTodayVisits = todayTeachers.length;
        const teacherActiveNow = todayTeachers.filter(t => !t.exit_time).length;
        
        // Unique teachers
        const uniqueTeachers = [...new Set(allTeachers.map(t => t.name))].length;
        
        // Average duration for today
        let totalDuration = 0;
        let count = 0;
        todayTeachers.forEach(t => {
            if (t.entry_time && t.exit_time) {
                const entry = new Date(`2000-01-01 ${t.entry_time}`);
                const exit = new Date(`2000-01-01 ${t.exit_time}`);
                totalDuration += (exit - entry) / 60000; // Convert to minutes
                count++;
            }
        });
        const teacherAvgDuration = count > 0 ? Math.round(totalDuration / count) : 0;
        
        // This month's visits
        const now = new Date();
        const thisMonth = now.getMonth() + 1;
        const thisYear = now.getFullYear();
        const thisMonthTeachers = allTeachers.filter(t => {
            if (!t.visit_date) return false;
            const visitDate = new Date(t.visit_date);
            return visitDate.getMonth() + 1 === thisMonth && visitDate.getFullYear() === thisYear;
        });
        const teacherThisMonth = thisMonthTeachers.length;
        
        // Update UI
        document.getElementById('teacherTotalVisits').textContent = teacherTotalVisits;
        document.getElementById('teacherTodayVisits').textContent = teacherTodayVisits;
        document.getElementById('teacherActiveNow').textContent = teacherActiveNow;
        document.getElementById('teacherUnique').textContent = uniqueTeachers;
        document.getElementById('teacherAvgDuration').textContent = teacherAvgDuration;
        document.getElementById('teacherThisMonth').textContent = teacherThisMonth;
        
    } catch (error) {
        console.error('Error loading teacher stats:', error);
    }
}

// ==================== DATE RANGE FUNCTIONS ====================

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

// ==================== ANALYTICS FUNCTIONS ====================

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

// ==================== CHART FUNCTIONS ====================

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
        
        // Course Distribution Chart
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
                    indexAxis: 'x',
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
            charts.level.update('none');
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
        
        // Duration Analysis
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
        
        // Course Chart
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
                            indexAxis: 'y',
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
                                    display: false
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
                            indexAxis: 'x',
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

// ==================== STUDENT VISITOR FUNCTIONS ====================

async function loadVisitors() {
    try {
        console.log("📋 Loading student visitors...");
        
        const table = document.getElementById('visitorTable');
        if (!table) {
            console.warn("⚠️ Visitor table not found");
            return;
        }
        
        // Show loading
        table.innerHTML = `
            <tr>
                <td colspan="13" class="loading-row">
                    <i class="fas fa-spinner fa-spin"></i>
                    <div>Loading student data...</div>
                </td>
            </tr>
        `;
        
        // Get filters
        const levelFilter = document.getElementById('levelFilter');
        const statusFilter = document.getElementById('statusFilter');
        const dataTypeFilter = document.getElementById('dataTypeFilter');
        
        // Build URL for student data
        let url = "/admin/visitors/filter";
        const params = new URLSearchParams();
        
        if (levelFilter && levelFilter.value) {
            params.append('level', levelFilter.value);
        }
        
        if (statusFilter && statusFilter.value === 'active') {
            params.append('status', 'active');
        } else if (statusFilter && statusFilter.value === 'exited') {
            params.append('status', 'exited');
        }
        
        // Apply date range
        if (currentDateRange.start && currentDateRange.end) {
            params.append('start_date', currentDateRange.start);
            params.append('end_date', currentDateRange.end);
        }
        
        if (params.toString()) {
            url = "/admin/analytics/advanced?" + params.toString();
        }
        
        const response = await fetch(url);
        
        if (response.status === 401) {
            window.location.href = "/admin/login";
            return;
        }
        
        let data = await response.json();
        
        // Handle analytics response format
        if (data.visitors) {
            allVisitors = data.visitors;
        } else {
            allVisitors = Array.isArray(data) ? data : [];
        }
        
        // Apply status filter if needed
        if (statusFilter && statusFilter.value === 'active') {
            allVisitors = allVisitors.filter(v => !v.exit_time);
        } else if (statusFilter && statusFilter.value === 'exited') {
            allVisitors = allVisitors.filter(v => v.exit_time);
        }
        
        totalRecords = allVisitors.length;
        
        if (allVisitors.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="13" class="loading-row">
                        <i class="fas fa-inbox"></i>
                        <div>No student visitors found</div>
                    </td>
                </tr>
            `;
            updateRecordCount(totalRecords);
            return;
        }
        
        renderTablePage();
        updateRecordCount(totalRecords);
        
        console.log("✅ Student visitors loaded successfully:", totalRecords);
        
    } catch (error) {
        console.error('❌ Error loading visitors:', error);
        const table = document.getElementById('visitorTable');
        if (table) {
            table.innerHTML = `
                <tr>
                    <td colspan="13" class="loading-row" style="color: #ef4444;">
                        <i class="fas fa-exclamation-triangle"></i>
                        <div>Error loading student data. Please try again.</div>
                    </td>
                </tr>
            `;
        }
        showNotification('Error loading student data', 'error');
    }
}

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
                    <div>No student visitors found</div>
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
    updatePagination();
    
    // Update select all checkbox
    const selectAll = document.getElementById('selectAll');
    if (selectAll) selectAll.checked = false;
    
    console.log("✅ Table page rendered");
}

function updateRecordCount(count) {
    const recordCountEl = document.getElementById('recordCount');
    if (recordCountEl) {
        recordCountEl.textContent = count;
    }
}

// ==================== TEACHER VISIT FUNCTIONS ====================

async function loadTeacherVisits() {
    try {
        console.log("👨‍🏫 Loading teacher visits...");
        
        const table = document.getElementById('teacherTable');
        if (!table) {
            console.warn("⚠️ Teacher table not found");
            return;
        }
        
        // Show loading
        table.innerHTML = `
            <tr>
                <td colspan="11" class="loading-row">
                    <i class="fas fa-spinner fa-spin"></i>
                    <div>Loading teacher data...</div>
                </td>
            </tr>
        `;
        
        // Get filters
        const statusFilter = document.getElementById('teacherFilter') || document.getElementById('statusFilter');
        const startDate = currentDateRange.start || '';
        const endDate = currentDateRange.end || '';
        
        // Build URL
        let url = '/admin/teachers/filter';
        const params = new URLSearchParams();
        
        if (statusFilter && statusFilter.value) {
            params.append('status', statusFilter.value);
        }
        
        if (startDate && endDate) {
            params.append('start_date', startDate);
            params.append('end_date', endDate);
        }
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url);
        
        if (response.status === 401) {
            window.location.href = '/admin/login';
            return;
        }
        
        const teachers = await response.json();
        
        allTeachers = Array.isArray(teachers) ? teachers : [];
        teacherTotalRecords = allTeachers.length;
        
        // Update teacher record count
        updateTeacherRecordCount(teacherTotalRecords);
        
        // Render teacher table
        renderTeacherTablePage();
        
        console.log("✅ Teacher visits loaded:", teacherTotalRecords);
        
    } catch (error) {
        console.error('❌ Error loading teacher visits:', error);
        const table = document.getElementById('teacherTable');
        if (table) {
            table.innerHTML = `
                <tr>
                    <td colspan="11" class="loading-row" style="color: #ef4444;">
                        <i class="fas fa-exclamation-triangle"></i>
                        <div>Error loading teacher data</div>
                    </td>
                </tr>
            `;
        }
        showNotification('Error loading teacher data', 'error');
    }
}

function renderTeacherTablePage() {
    console.log("📄 Rendering teacher page", currentTeacherPage);
    
    const table = document.getElementById('teacherTable');
    if (!table) return;
    
    const startIndex = (currentTeacherPage - 1) * teacherPageSize;
    const endIndex = Math.min(startIndex + teacherPageSize, teacherTotalRecords);
    const pageTeachers = allTeachers.slice(startIndex, endIndex);
    
    if (pageTeachers.length === 0) {
        table.innerHTML = `
            <tr>
                <td colspan="11" class="loading-row">
                    <i class="fas fa-inbox"></i>
                    <div>No teacher visits found</div>
                </td>
            </tr>
        `;
        return;
    }
    
    let tableHTML = '';
    
    pageTeachers.forEach(t => {
        tableHTML += `
            <tr>
                <td class="checkbox-cell">
                    <input type="checkbox" class="teacher-row-checkbox" value="${t.id}">
                </td>
                <td><strong>${t.name}</strong></td>
                <td>${t.employee_id || '-'}</td>
                <td>${t.purpose}</td>
                <td>${t.entry_time || '-'}</td>
                <td>${t.exit_time || '-'}</td>
                <td>${t.visit_date}</td>
                <td>${t.visit_day}</td>
                <td>${t.notes || '-'}</td>
                <td>
                    <span class="status-badge ${t.exit_time ? 'exited' : 'active'}">
                        <i class="fas ${t.exit_time ? 'fa-door-closed' : 'fa-door-open'}"></i>
                        ${t.exit_time ? 'Exited' : 'Active'}
                    </span>
                </td>
                <td>
                    ${!t.exit_time ? `
                        <button class="btn-exit" onclick="markTeacherExit(${t.id})">
                            <i class="fas fa-sign-out-alt"></i> Exit
                        </button>
                    ` : ''}
                    <button class="btn btn-secondary view-details-btn" onclick="viewTeacherDetails(${t.id})" style="margin-left: 5px; padding: 6px 10px; font-size: 12px;">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    table.innerHTML = tableHTML;
    
    // Update teacher pagination
    updateTeacherPagination();
    
    // Update select all checkbox
    const selectAll = document.getElementById('selectAllTeachers');
    if (selectAll) selectAll.checked = false;
    
    console.log("✅ Teacher table page rendered");
}

function updateTeacherRecordCount(count) {
    const recordCountEl = document.getElementById('teacherRecordCount');
    if (recordCountEl) {
        recordCountEl.textContent = count;
    }
}

function updateTeacherPagination() {
    const currentPageEl = document.getElementById('teacherCurrentPage');
    const totalPagesEl = document.getElementById('teacherTotalPages');
    const prevBtn = document.getElementById('prevTeacherBtn');
    const nextBtn = document.getElementById('nextTeacherBtn');
    
    if (currentPageEl) currentPageEl.textContent = currentTeacherPage;
    if (totalPagesEl) totalPagesEl.textContent = Math.ceil(teacherTotalRecords / teacherPageSize) || 1;
    
    if (prevBtn) prevBtn.disabled = currentTeacherPage === 1;
    if (nextBtn) nextBtn.disabled = currentTeacherPage * teacherPageSize >= teacherTotalRecords;
}

function prevTeacherPage() {
    if (currentTeacherPage > 1) {
        currentTeacherPage--;
        renderTeacherTablePage();
    }
}

function nextTeacherPage() {
    if (currentTeacherPage * teacherPageSize < teacherTotalRecords) {
        currentTeacherPage++;
        renderTeacherTablePage();
    }
}

// ==================== PAGINATION & SELECTION ====================

function updatePagination() {
    const currentPageEl = document.getElementById('currentPage');
    const totalPagesEl = document.getElementById('totalPages');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (currentPageEl) currentPageEl.textContent = currentPage;
    if (totalPagesEl) totalPagesEl.textContent = Math.ceil(totalRecords / pageSize) || 1;
    
    if (prevBtn) prevBtn.disabled = currentPage === 1;
    if (nextBtn) nextBtn.disabled = currentPage * pageSize >= totalRecords;
}

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

function toggleSelectAllTeachers() {
    const selectAll = document.getElementById('selectAllTeachers');
    if (!selectAll) return;
    
    const isChecked = selectAll.checked;
    document.querySelectorAll('.teacher-row-checkbox').forEach(cb => {
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

function selectAllTeacherRows() {
    const selectAll = document.getElementById('selectAllTeachers');
    if (selectAll) {
        selectAll.checked = true;
        document.querySelectorAll('.teacher-row-checkbox').forEach(cb => {
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

function getSelectedTeacherIds() {
    const selected = [];
    document.querySelectorAll('.teacher-row-checkbox:checked').forEach(cb => {
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
        alert('Please select at least one student visitor');
        return;
    }
    
    if (!action) {
        alert('Please select an action');
        return;
    }
    
    if (action === 'delete' && !confirm(`Are you sure you want to delete ${visitorIds.length} student visitors? This action cannot be undone.`)) {
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
            loadAnalytics();
            loadDailyStats();
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        console.error('Bulk action error:', error);
        showNotification('Error performing bulk action', 'error');
    }
}

async function applyTeacherBulkAction() {
    const bulkActionSelect = document.getElementById('teacherBulkAction');
    if (!bulkActionSelect) return;
    
    const action = bulkActionSelect.value;
    const teacherIds = getSelectedTeacherIds();
    
    if (teacherIds.length === 0) {
        alert('Please select at least one teacher visit');
        return;
    }
    
    if (!action) {
        alert('Please select an action');
        return;
    }
    
    if (action === 'mark_exit') {
        if (!confirm(`Are you sure you want to mark ${teacherIds.length} teacher visits as exited?`)) {
            return;
        }
        
        try {
            let successCount = 0;
            for (const teacherId of teacherIds) {
                const response = await fetch(`/admin/teachers/mark_exit/${teacherId}`, {
                    method: 'PUT'
                });
                
                if (response.ok) {
                    successCount++;
                }
            }
            
            showNotification(`Marked ${successCount} teacher visits as exited`, 'success');
            loadTeacherVisits();
            loadTeacherStats();
        } catch (error) {
            console.error('Teacher bulk action error:', error);
            showNotification('Error performing bulk action', 'error');
        }
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
    const dataTypeFilter = document.getElementById('dataTypeFilter');
    const teacherFilter = document.getElementById('teacherFilter');
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    
    if (levelFilter) levelFilter.value = '';
    if (statusFilter) statusFilter.value = '';
    if (dataTypeFilter) dataTypeFilter.value = 'students';
    if (teacherFilter) teacherFilter.value = '';
    
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
    currentTeacherPage = 1;
    
    loadAnalytics();
    loadVisitors();
    loadTeacherVisits();
    
    // Refresh stats based on active tab
    if (document.getElementById('dailyStats').classList.contains('active')) {
        loadDailyStats();
    } else if (document.getElementById('lifetimeStats').classList.contains('active')) {
        loadLifetimeStats();
    } else if (document.getElementById('teacherStats').classList.contains('active')) {
        loadTeacherStats();
    }
}

// ==================== VISITOR ACTIONS ====================

async function markExit(visitorId) {
    if (!confirm('Mark this student visitor as exited?')) return;
    
    try {
        const response = await fetch(`/student/exit/${visitorId}`, { method: 'PUT' });
        
        if (response.ok) {
            showNotification('Exit marked successfully!', 'success');
            loadVisitors();
            loadAnalytics();
            loadDailyStats();
        } else {
            const data = await response.json();
            showNotification(data.error || 'Failed to mark exit', 'error');
        }
    } catch (error) {
        console.error('Error marking exit:', error);
        showNotification('Error marking exit', 'error');
    }
}

async function markTeacherExit(teacherId) {
    if (!confirm('Mark this teacher visit as exited?')) return;
    
    try {
        const response = await fetch(`/admin/teachers/mark_exit/${teacherId}`, {
            method: 'PUT'
        });
        
        if (response.ok) {
            showNotification('Teacher exit marked successfully!', 'success');
            loadTeacherVisits();
            loadTeacherStats();
        } else {
            const data = await response.json();
            showNotification(data.error || 'Failed to mark teacher exit', 'error');
        }
    } catch (error) {
        console.error('Error marking teacher exit:', error);
        showNotification('Error marking teacher exit', 'error');
    }
}

function viewDetails(visitorId) {
    const visitor = allVisitors.find(v => v.id === visitorId);
    if (!visitor) {
        alert('Student visitor not found');
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
    
    showModal('Student Visitor Details', details);
}

function viewTeacherDetails(teacherId) {
    const teacher = allTeachers.find(t => t.id === teacherId);
    if (!teacher) {
        alert('Teacher visit not found');
        return;
    }
    
    const details = `
        <div style="text-align: left;">
            <p><strong>Name:</strong> ${teacher.name}</p>
            <p><strong>Employee ID:</strong> ${teacher.employee_id || 'N/A'}</p>
            <p><strong>Purpose:</strong> ${teacher.purpose}</p>
            <p><strong>Notes:</strong> ${teacher.notes || 'No additional notes'}</p>
            <p><strong>Entry Time:</strong> ${teacher.entry_time || 'N/A'}</p>
            <p><strong>Exit Time:</strong> ${teacher.exit_time || 'Not exited yet'}</p>
            <p><strong>Visit Date:</strong> ${teacher.visit_date}</p>
            <p><strong>Day:</strong> ${teacher.visit_day || 'N/A'}</p>
            <p><strong>Record ID:</strong> ${teacher.id}</p>
        </div>
    `;
    
    showModal('Teacher Visit Details', details);
}

// ==================== EXPORT FUNCTIONS ====================

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
