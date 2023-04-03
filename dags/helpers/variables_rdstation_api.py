# ### email and phone Must be a array type ###
_create_contacts_sql_table = """
    CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        _id VARCHAR(255),
        title VARCHAR(255) NULL,
        facebook VARCHAR(255) NULL,
        linkedin VARCHAR(255) NULL,
        skype VARCHAR(255) NULL,
        created_at TIMESTAMP NULL,
        updated_at TIMESTAMP NULL,
        email VARCHAR(255) NULL, 
        phone VARCHAR(255) NULL
    );
"""
_contacts_colum_names = [
    "_id",
    "title",
    "facebook",
    "linkedin",
    "skype",
    "created_at",
    "updated_at",
    "email",
    "phone",
]
