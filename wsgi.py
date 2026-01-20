from backend.app import create_app

# Create app instance
app = create_app()

# Initialize database on first load
try:
    from backend.supabase_db import SupabaseDatabase
    SupabaseDatabase.init_database()
except Exception as e:
    print(f"⚠️ Database init warning: {e}")

if __name__ == "__main__":
    app.run(debug=False)
