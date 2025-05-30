-- Feedback table
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on user_id for faster queries
CREATE INDEX idx_feedback_user_id ON feedback(user_id);

-- Update timestamp trigger for feedback table
CREATE OR REPLACE TRIGGER update_feedback_modtime
    BEFORE UPDATE ON feedback
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column(); 