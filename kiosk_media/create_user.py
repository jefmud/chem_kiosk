import config

config.set_users_file("users.json")

email = raw_input("Enter username EMAIL: ")
if '@' in email:
    password = raw_input("Enter password: ")
    if len(password) > 4:
        email = email.strip()
        password = password.strip()
        config.user_add(email, password)
        print "email {} was added with password.".format(email)
    else:
       print "Password was too short. Aborting."
else:
    print("Aborting")