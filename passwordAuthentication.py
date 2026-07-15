import bcrypt
users = {}

def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def verify_password(password, stored_hash):
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash)


def register_user():
    username = input("Enter Username: ")

    if username in users:
        print("User already exists.")
        return

    password = input("Enter Password: ")

    hashed_password = hash_password(password)

    users[username] = hashed_password

    print("\nUser Registered Successfully")
    print("Stored Password Hash:")
    print(hashed_password.decode())


def authenticate_user():
    username = input("Enter Username: ")
    password = input("Enter Password: ")

    stored_hash = users.get(username)

    if stored_hash is None:
        print("Authentication Failed")
        return

    if verify_password(password, stored_hash):
        print("Authentication Successful")
    else:
        print("Authentication Failed")


def main():
    while True:
        print("\n===== Password-Based Authentication =====")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter Choice: ")

        if choice == "1":
            register_user()

        elif choice == "2":
            authenticate_user()

        elif choice == "3":
            print("Program Ended.")
            break

        else:
            print("Invalid Choice")

if __name__ == "__main__":
    main()