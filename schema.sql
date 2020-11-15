CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT, password TEXT, admin BOOLEAN);
CREATE TABLE categories (id SERIAL PRIMARY KEY, title TEXT);
CREATE TABLE threads (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users, category_id INTEGER REFERENCES categories, title TEXT, private BOOLEAN, created_at TIMESTAMP);
CREATE TABLE messages (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users, thread_id INTEGER REFERENCES threads, content TEXT, sent_at TIMESTAMP);
CREATE TABLE allowedusers (id SERIAL PRIMARY KEY, thread_id INTEGER REFERENCES threads, user1_id INTEGER REFERENCES users, user2_id INTEGER REFERENCES users);
