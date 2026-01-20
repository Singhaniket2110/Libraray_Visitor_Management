from flask import Flask, render_template, session
from backend.config import Config
import os

def create_app():
    # Get the base directory
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    app = Flask(__name__, 
                template_folder=os.path.join(basedir, 'templates'),
                static_folder=os.path.join(basedir, 'static'))
    
    # Load configuration
    app.config.from_object(Config)
    
    print("✅ Flask app initialized")
    
    # ==================== HEALTH & TEST ROUTES ====================
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'message': 'Library System API is running'}
    
    @app.route('/test')
    def test():
        return {
            'session_working': True,
            'session_type': 'cookie-based',
            'app_ready': True
        }
    
    @app.route('/db-test')
    def db_test():
        try:
            from backend.supabase_db import SupabaseDatabase
            result = SupabaseDatabase.execute_query("SELECT COUNT(*) as count FROM admin", fetch=True)
            return {
                'db_status': 'connected',
                'admin_count': result['count'] if result else 0
            }
        except Exception as e:
            return {'db_status': 'error', 'message': str(e)}, 500
    
    # ==================== REGISTER BLUEPRINTS ====================
    
    try:
        from backend.routes.student_routes import student_bp
        from backend.routes.admin_routes import admin_bp
        
        app.register_blueprint(student_bp)
        app.register_blueprint(admin_bp)
        
        print("✅ Blueprints registered")
    except Exception as e:
        print(f"❌ Blueprint registration error: {e}")
    
    # ==================== HOME ROUTE ====================
    
    @app.route('/')
    def index():
        return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Library Visitor Management</title>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<style>
:root {
    --primary: #6366f1;
    --secondary: #8b5cf6;
    --dark: #1e293b;
    --light: #f8fafc;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

body {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    overflow-x: hidden;
}

/* ================= MAIN CONTAINER ================= */

.main-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px;
}

/* ================= HERO CARD ================= */

.hero {
    background: rgba(255, 255, 255, 0.97);
    padding: 70px 60px;
    border-radius: 32px;
    max-width: 1100px;
    width: 100%;
    text-align: center;
    box-shadow: 0 35px 70px rgba(0,0,0,0.3);
}

/* ================= COLLEGE HEADER ================= */

.college-header {
    margin-bottom: 40px;
    border-bottom: 3px solid #e2e8f0;
    padding-bottom: 25px;
}

.college-logo {
    width: 150px;
    height: 150px;
    margin: 0 auto 20px;
    border-radius: 50%;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}

.college-logo img {
    width: 85%;
    height: 85%;
    object-fit: contain;
}

.college-name {
    font-size: 1.6rem;
    font-weight: 800;
    color: #1e293b;
}

.college-subtitle {
    margin-top: 10px;
    font-size: 1.2rem;
    font-style: italic;
    color: #6366f1;
}

/* ================= FIXED LIBRARY HEADING ================= */

.library-heading {
    margin: 40px 0 25px;
    line-height: 1.25;
}

.library-name {
    display: block;
    font-size: 2.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.library-subtitle {
    display: block;
    margin-top: 12px;
    font-size: 1.45rem;
    font-weight: 600;
    color: #475569;
}

/* ================= DESCRIPTION ================= */

.hero p {
    margin: 25px auto 50px;
    max-width: 750px;
    font-size: 1.15rem;
    color: #64748b;
    line-height: 1.8;
}

/* ================= BUTTONS ================= */

.hero-buttons {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}

.hero-btn {
    padding: 20px;
    color: white;
    border-radius: 16px;
    text-decoration: none;
    font-weight: 700;
    display: flex;
    gap: 12px;
    justify-content: center;
    align-items: center;
    transition: 0.3s;
}

.hero-btn:hover {
    transform: translateY(-5px);
}

.hero-btn:nth-child(1) { background: #6366f1; }
.hero-btn:nth-child(2) { background: #f59e0b; }
.hero-btn:nth-child(3) { background: #ef4444; }
.hero-btn:nth-child(4) { background: #10b981; }
.hero-btn:nth-child(5) { background: #8b5cf6; }
.hero-btn:nth-child(6) { background: #ec4899; }
.hero-btn:nth-child(7) { background: #3b82f6; grid-column: 2; }

/* ================= MOBILE ================= */

@media (max-width: 768px) {
    .hero { padding: 45px 25px; }
    .library-name { font-size: 2rem; }
    .library-subtitle { font-size: 1.15rem; }
    .hero-buttons { grid-template-columns: 1fr; }
    .hero-btn:nth-child(7) { grid-column: auto; }
}

@media (max-width: 480px) {
    .library-name { font-size: 1.7rem; }
    .library-subtitle { font-size: 1rem; }
}
</style>
</head>

<body>

<div class="main-container">
<div class="hero">

    <div class="college-header">
        <div class="college-logo">
            <img src="https://nesedu.in/wp-content/uploads/2025/03/d_logo@4x.png">
        </div>
        <div class="college-name">
            Navneet Education Society's<br>
            Navneet College of Arts, Science & Commerce
        </div>
        <div class="college-subtitle">"विद्या ददाति विनयं"</div>
    </div>

    <div class="library-heading">
        <span class="library-name">
            Smt Kesardevi Mishra Memorial Library
        </span>
        <span class="library-subtitle">
            Visitor and Digital Resource Management System
        </span>
    </div>

    <p>
        Welcome to our advanced library management platform designed to streamline visitor tracking,
        enhance security, and digitize library operations for modern academic institutions.
    </p>

    <div class="hero-buttons">
        <a href="/student/" class="hero-btn"><i class="fas fa-graduation-cap"></i> Student Entry</a>
        <a href="/admin/login" class="hero-btn"><i class="fas fa-lock"></i> Admin Login</a>
        <a href="/student/exit" class="hero-btn"><i class="fas fa-door-open"></i> Exit</a>
        <a href="/about" class="hero-btn"><i class="fas fa-book"></i> About</a>
        <a href="/services" class="hero-btn"><i class="fas fa-cloud"></i> Services</a>
        <a href="/guide" class="hero-btn"><i class="fas fa-info-circle"></i> Guide</a>
        <a href="/developer" class="hero-btn"><i class="fas fa-laptop-code"></i> Developer</a>
    </div>

</div>
</div>

</body>
</html>
'''
    
    # ==================== OTHER PAGE ROUTES ====================
    
    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/developer')
    def developer():
        return render_template('developer.html')

    @app.route('/guide')
    def guide():
        return render_template('guide.html')
    
    @app.route('/services')
    def services():
        return render_template('library_services.html')
    
    # ==================== ERROR HANDLERS ====================
    
    @app.errorhandler(404)
    def not_found(e):
        return '''<!DOCTYPE html>
<html>
<head><title>404 - Page Not Found</title></head>
<body style="font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f8fafc;">
    <div style="text-align: center;">
        <h1 style="font-size: 72px; margin: 0; color: #ef4444;">404</h1>
        <p style="font-size: 24px; color: #64748b;">Page Not Found</p>
        <a href="/" style="color: #6366f1; text-decoration: none; font-weight: bold;">← Go Home</a>
    </div>
</body>
</html>''', 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return '''<!DOCTYPE html>
<html>
<head><title>500 - Server Error</title></head>
<body style="font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f8fafc;">
    <div style="text-align: center;">
        <h1 style="font-size: 72px; margin: 0; color: #ef4444;">500</h1>
        <p style="font-size: 24px; color: #64748b;">Internal Server Error</p>
        <a href="/" style="color: #6366f1; text-decoration: none; font-weight: bold;">← Go Home</a>
    </div>
</body>
</html>''', 500

    return app

