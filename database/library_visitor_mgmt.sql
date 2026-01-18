-- Drop existing database and create fresh
DROP DATABASE IF EXISTS library_visitor_mgmt;
CREATE DATABASE library_visitor_mgmt;
USE library_visitor_mgmt;

-- Admin Table
CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin
INSERT INTO admin (username, password) VALUES
('admin', 'admin123');

-- Visitors Table (Main Table) - UPDATED FOR JC, UG, PG
CREATE TABLE visitors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Basic Info
    name VARCHAR(100) NOT NULL,
    roll_no VARCHAR(20) NOT NULL,
    
    -- Education Info - FIXED FOR YOUR REQUIREMENTS
    level ENUM('JC','UG','PG') NOT NULL,
    course VARCHAR(100) NOT NULL,
    year VARCHAR(20),  -- For UG/PG only (First Year, Second Year, Third Year)
    
    -- JC Specific Fields
    jc_year VARCHAR(10),      -- FYJC or SYJC
    jc_stream VARCHAR(20),    -- Science, Arts, Commerce
    
    purpose VARCHAR(100) NOT NULL,
    
    -- Time Tracking
    entry_time TIME DEFAULT (CURRENT_TIME),
    exit_time TIME,
    visit_date DATE DEFAULT (CURRENT_DATE),
    visit_day VARCHAR(10) NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_visit_date (visit_date),
    INDEX idx_level (level),
    INDEX idx_roll_no (roll_no)
);

-- Create views for reports
CREATE VIEW today_stats AS
SELECT 
    COUNT(*) as total_visitors,
    COUNT(CASE WHEN exit_time IS NULL THEN 1 END) as currently_inside,
    COUNT(CASE WHEN level = 'JC' THEN 1 END) as jc_visitors,
    COUNT(CASE WHEN level = 'UG' THEN 1 END) as ug_visitors,
    COUNT(CASE WHEN level = 'PG' THEN 1 END) as pg_visitors
FROM visitors
WHERE visit_date = CURRENT_DATE;

CREATE VIEW active_visitors AS
SELECT 
    v.*,
    TIMEDIFF(CURRENT_TIME, v.entry_time) as duration_inside
FROM visitors v
WHERE v.exit_time IS NULL 
AND v.visit_date = CURRENT_DATE
ORDER BY v.entry_time DESC;

-- Print success message
SELECT '✅ Database created successfully with EXACT requirements!' as message;