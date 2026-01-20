from backend.app import create_app

# Create app
app = create_app()

# Initialize database
try:
    from backend.supabase_db import SupabaseDatabase
    SupabaseDatabase.init_database()
except Exception as e:
    print(f"⚠️ Database init: {e}")

if __name__ == "__main__":
    app.run(debug=False)
