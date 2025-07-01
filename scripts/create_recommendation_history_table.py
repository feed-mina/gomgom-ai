# -*- coding: utf-8 -*-
import psycopg2
from psycopg2.extras import RealDictCursor

def create_recommendation_history_table():
    """Create RecommendationHistory table."""
    
    # Database connection
    conn = psycopg2.connect(
        dbname="gomgom_ai",
        user="postgres",
        password="postgres1234",
        host="localhost",
        port="5432"
    )
    
    cur = conn.cursor()
    
    try:
        # Create RecommendationHistory table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS recommendation_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            request_type VARCHAR(32) NOT NULL,
            input_data JSONB NOT NULL,
            result_data JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        cur.execute(create_table_sql)
        
        # Create indexes
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS ix_recommendation_history_id 
        ON recommendation_history (id);
        """
        
        cur.execute(create_index_sql)
        
        # Index for user queries
        create_user_index_sql = """
        CREATE INDEX IF NOT EXISTS ix_recommendation_history_user_id 
        ON recommendation_history (user_id);
        """
        
        cur.execute(create_user_index_sql)
        
        # Index for request type queries
        create_type_index_sql = """
        CREATE INDEX IF NOT EXISTS ix_recommendation_history_request_type 
        ON recommendation_history (request_type);
        """
        
        cur.execute(create_type_index_sql)
        
        # Index for date queries
        create_date_index_sql = """
        CREATE INDEX IF NOT EXISTS ix_recommendation_history_created_at 
        ON recommendation_history (created_at);
        """
        
        cur.execute(create_date_index_sql)
        
        conn.commit()
        print("✅ RecommendationHistory table created successfully.")
        
    except Exception as e:
        conn.rollback()
        # Print(f"❌ Error creating table: {e}")
        
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_recommendation_history_table() 