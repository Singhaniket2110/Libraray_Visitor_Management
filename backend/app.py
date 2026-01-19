from flask import Flask, render_template, session
from flask_session import Session
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
    
    # ✅ IMPORTANT: Initialize Session BEFORE any route
    # This fixes Vercel session issues
    Session(app)
    
    print("✅ Flask app initialized with session support")
    
    # Test route
    @app.route('/test')
    def test():
        return {
            'session_working': True,
            'session_id': session.sid if hasattr(session, 'sid') else 'N/A',
            'session_type': app.config.get('SESSION_TYPE', 'unknown')
        }
    
    # Health check
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'message': 'Library System API is running'}
    
    # Database test
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
            return {'db_status': 'error', 'message': str(e)}
    
    # Import and register blueprints
    from backend.routes.student_routes import student_bp
    from backend.routes.admin_routes import admin_bp
    
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    
    print("✅ Blueprints registered")
    
    # Home route (your hardcoded HTML)
    @app.route('/')
    def index():
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Library Visitor Management</title>
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
            padding: 0;
            position: relative;
            overflow-x: hidden;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(255, 255, 255, 0.15) 0%, transparent 25%),
                radial-gradient(circle at 90% 80%, rgba(255, 255, 255, 0.15) 0%, transparent 25%);
            animation: float 20s infinite ease-in-out;
            pointer-events: none;
            z-index: 1;
        }
        
        @keyframes float {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            33% { transform: translate(-15px, -10px) rotate(1deg); }
            66% { transform: translate(15px, 10px) rotate(-1deg); }
        }
        
        .main-container {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            position: relative;
            z-index: 2;
        }
        
        .hero {
            text-align: center;
            background: rgba(255, 255, 255, 0.97);
            backdrop-filter: blur(30px);
            padding: 80px 70px;
            border-radius: 32px;
            box-shadow: 
                0 35px 70px rgba(0, 0, 0, 0.3),
                0 0 0 1px rgba(255, 255, 255, 0.25),
                inset 0 0 50px rgba(255, 255, 255, 0.5);
            max-width: 1100px;
            width: 100%;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.4);
            animation: fadeInUp 0.8s ease;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(40px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 8px;
            background: linear-gradient(90deg, 
                #6366f1 0%, 
                #8b5cf6 25%, 
                #ec4899 50%, 
                #8b5cf6 75%, 
                #6366f1 100%);
            background-size: 200% 100%;
            animation: shimmer 3s infinite linear;
        }
        
        @keyframes shimmer {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        .hero::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 120%;
            height: 120%;
            background: radial-gradient(circle, rgba(99, 102, 241, 0.05) 0%, transparent 70%);
            z-index: -1;
            pointer-events: none;
        }
        
        .college-header {
            margin-bottom: 50px;
            padding-bottom: 30px;
            border-bottom: 3px solid rgba(226, 232, 240, 0.8);
            position: relative;
        }
        
        .college-header::after {
            content: '';
            position: absolute;
            bottom: -3px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 3px;
            background: linear-gradient(90deg, transparent, #6366f1, transparent);
        }
        
        .college-logo-container {
            position: relative;
            width: 160px;
            height: 160px;
            margin: 0 auto 25px;
        }
        
        .college-logo {
            width: 100%;
            height: 100%;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 
                0 20px 40px rgba(0, 0, 0, 0.15),
                0 0 0 8px rgba(255, 255, 255, 0.8),
                0 0 0 12px rgba(99, 102, 241, 0.1);
            animation: pulse 3s infinite ease-in-out;
            position: relative;
            overflow: hidden;
        }
        
        .college-logo::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(transparent, rgba(99, 102, 241, 0.1), transparent 30%);
            animation: rotate 10s linear infinite;
        }
        
        @keyframes rotate {
            100% { transform: rotate(360deg); }
        }
        
        .college-logo img {
            width: 85%;
            height: 85%;
            object-fit: contain;
            border-radius: 50%;
            position: relative;
            z-index: 2;
            background: white;
            padding: 5px;
        }
        
        @keyframes pulse {
            0%, 100% { 
                transform: scale(1);
                box-shadow: 
                    0 20px 40px rgba(0, 0, 0, 0.15),
                    0 0 0 8px rgba(255, 255, 255, 0.8),
                    0 0 0 12px rgba(99, 102, 241, 0.1);
            }
            50% { 
                transform: scale(1.03);
                box-shadow: 
                    0 25px 50px rgba(0, 0, 0, 0.2),
                    0 0 0 8px rgba(255, 255, 255, 0.9),
                    0 0 0 12px rgba(99, 102, 241, 0.15);
            }
        }
        
        .college-name {
            font-size: 1.8rem;
            font-weight: 800;
            color: var(--dark);
            margin-bottom: 8px;
            line-height: 1.3;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.5px;
        }
        
        .college-subtitle {
            font-size: 1.3rem;
            color: #6366f1;
            font-weight: 600;
            margin-top: 12px;
            font-style: italic;
            padding: 8px 24px;
            background: rgba(99, 102, 241, 0.08);
            border-radius: 50px;
            display: inline-block;
            border: 2px solid rgba(99, 102, 241, 0.2);
        }
        
        .hero-icon {
            font-size: 90px;
            margin: 40px 0;
            display: inline-block;
            animation: floatIcon 3s infinite ease-in-out;
            filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.1));
        }
        
        @keyframes floatIcon {
            0%, 100% { 
                transform: translateY(0) rotate(0deg); 
                filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.1));
            }
            50% { 
                transform: translateY(-20px) rotate(5deg); 
                filter: drop-shadow(0 20px 30px rgba(0, 0, 0, 0.2));
            }
        }
        
        .hero h1 {
            color: var(--dark);
            margin-bottom: 25px;
            font-size: 3.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, 
                #6366f1 0%, 
                #8b5cf6 33%, 
                #ec4899 66%, 
                #6366f1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            background-size: 300% 100%;
            animation: gradientShift 8s infinite linear;
            letter-spacing: -1px;
            line-height: 1.1;
        }
        
        @keyframes gradientShift {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .hero p {
            color: #64748b;
            margin-bottom: 60px;
            font-size: 1.2rem;
            line-height: 1.8;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
            font-weight: 500;
        }
        
        .hero-buttons {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .hero-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 22px 18px;
            color: white;
            text-decoration: none;
            border-radius: 16px;
            font-weight: 700;
            font-size: 0.95rem;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 12px 25px rgba(0, 0, 0, 0.2);
            border: 3px solid transparent;
            position: relative;
            overflow: hidden;
            min-height: 75px;
        }
        
        .hero-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.7s ease;
        }
        
        .hero-btn:hover::before {
            left: 100%;
        }
        
        .hero-btn:hover {
            transform: translateY(-6px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
        }
        
        .hero-btn:active {
            transform: translateY(-3px) scale(1.01);
        }
        
        .hero-btn i {
            font-size: 1.5rem;
            min-width: 30px;
            text-align: center;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
        }
        
        .hero-btn span {
            flex: 1;
            text-align: center;
            font-size: 0.95rem;
            line-height: 1.3;
        }
        
        /* Button Colors */
        .hero-btn:nth-child(1) {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        }
        
        .hero-btn:nth-child(2) {
            background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
        }
        
        .hero-btn:nth-child(3) {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }
        
        .hero-btn:nth-child(4) {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }
        
        .hero-btn:nth-child(5) {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        }
        
        .hero-btn:nth-child(6) {
            background: linear-gradient(135deg, #ec4899 0%, #db2777 100%);
        }
        
        .hero-btn:nth-child(7) {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            grid-column: 2 / 3;
        }
        
        /* Responsive Design */
        @media (max-width: 968px) {
            .hero-buttons {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .hero-btn:nth-child(7) {
                grid-column: auto;
            }
        }
        
        @media (max-width: 768px) {
            .main-container {
                padding: 20px;
            }
            
            .hero {
                padding: 50px 30px;
                border-radius: 24px;
            }
            
            .college-logo-container {
                width: 130px;
                height: 130px;
            }
            
            .college-name {
                font-size: 1.4rem;
            }
            
            .college-subtitle {
                font-size: 1.1rem;
                padding: 6px 18px;
            }
            
            .hero h1 {
                font-size: 2.5rem;
            }
            
            .hero p {
                font-size: 1.1rem;
                margin-bottom: 40px;
            }
            
            .hero-buttons {
                gap: 15px;
            }
            
            .hero-btn {
                padding: 18px 15px;
                min-height: 70px;
                font-size: 0.9rem;
            }
            
            .hero-btn i {
                font-size: 1.3rem;
            }
            
            .hero-icon {
                font-size: 70px;
                margin: 30px 0;
            }
        }
        
        @media (max-width: 480px) {
            .hero {
                padding: 40px 20px;
            }
            
            .college-name {
                font-size: 1.2rem;
            }
            
            .college-subtitle {
                font-size: 1rem;
            }
            
            .hero h1 {
                font-size: 2rem;
            }
            
            .hero p {
                font-size: 1rem;
            }
            
            .hero-buttons {
                grid-template-columns: 1fr;
                gap: 12px;
            }
            
            .hero-btn {
                padding: 18px 15px;
                min-height: 65px;
            }
            
            .hero-btn i {
                font-size: 1.3rem;
            }
            
            .hero-btn span {
                font-size: 0.9rem;
            }
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="main-container">
        <div class="hero">
            <div class="college-header">
                <div class="college-logo-container">
                    <div class="college-logo">
                        <img src="https://nesedu.in/wp-content/uploads/2025/03/d_logo@4x.png" 
                             alt="College Logo" 
                             onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYwIiBoZWlnaHQ9IjE2MCIgdmlld0JveD0iMCAwIDE2MCAxNjAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxjaXJjbGUgY3g9IjgwIiBjeT0iODAiIHI9IjcwIiBmaWxsPSIjNjM2NmYxIi8+Cjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjMyIiBmaWxsPSJ3aGl0ZSI+TkVTPC90ZXh0Pgo8L3N2Zz4K'">
                    </div>
                </div>
                <div class="college-name">Navneet Education Society's<br>Navneet College of Arts, Science & Commerce</div>
                <div class="college-subtitle">"विद्या ददाति विनयं"</div>
            </div>
            
            <div class="hero-icon">📚</div>
            <h1>Library Visitor Management System</h1>
            <p>Welcome to our advanced library management platform. Streamline visitor tracking, enhance security, and optimize library operations with our intuitive, feature-rich system designed for modern educational institutions.</p>
            
            <div class="hero-buttons">
                <a href="/student/" class="hero-btn">
                    <i class="fas fa-graduation-cap"></i>
                    <span>Student Entry Portal</span>
                </a>
                <a href="/admin/login" class="hero-btn">
                    <i class="fas fa-lock"></i>
                    <span>Admin Dashboard</span>
                </a>
                <a href="/student/exit" class="hero-btn">
                    <i class="fas fa-door-open"></i>
                    <span>Student Exit Portal</span>
                </a>
                <a href="/about" class="hero-btn">
                    <i class="fas fa-book"></i>
                    <span>About Our Library</span>
                </a>
                <a href="/services" class="hero-btn">
                    <i class="fas fa-cloud"></i>
                    <span>Library Services</span>
                </a>
                <a href="/guide" class="hero-btn">
                    <i class="fas fa-info-circle"></i>
                    <span>How to Use System</span>
                </a>
                <a href="/developer" class="hero-btn">
                    <i class="fas fa-laptop-code"></i>
                    <span>About Developer</span>
                </a>
            </div>
        </div>
    </div>
</body>
</html>'''
    
    # About page route
    @app.route('/about')
    def about():
        return render_template('about.html')
    
    # Developer page route
    @app.route('/developer')
    def developer():
        return render_template('developer.html')

    # Guide page route  
    @app.route('/guide')
    def guide():
        return render_template('guide.html')
    
    # Library Services page route  
    @app.route('/services')
    def services():
        return render_template('library_services.html')
    
    # Health check endpoint for Vercel
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'message': 'Library Visitor System is running on Vercel'}
    
    # Error handlers
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
