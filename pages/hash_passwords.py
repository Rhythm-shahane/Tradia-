import streamlit_authenticator as stauth

# List of plain-text passwords
passwords = ['1234', 'adminpass']

# Create Hasher instance
hasher = stauth.Hasher()

# Hash each password individually
hashed_passwords = [hasher.hash(pw) for pw in passwords]

# Print hashed passwords
for i, hashed in enumerate(hashed_passwords, 1):
    print(f"Hashed Password {i}: {hashed}")
