# Server Configuration
1. RDP into the terminal server.
2. Launch `Server Manager` as an Administrator.
3. Select `Add roles and features`.
4. Choose installation type `Role-based or feature-based installation`.
5. Select the `Windows Server 2012 R2 Standard` server.
6. From the Server Roles window make sure `Remote Desktop Services` is selected.
7. From the Features window just use the defaults.
8. From the Role Services window you should have `Remote Desktop Licensing` and `Remote Desktop Session Host` selected.
9. You will get a prompt when selecting each role make sure `Include management tools` is checked before clicking `Add Features`.
10. Click `Install` and then reboot the server after installation has completed.

# Adding Users
1. Navigate to `Control Panel\User Accounts\User Accounts\Manage Accounts`.
2. Create a new `Local User` account.
3. Navigate to `Control Panel\System and Security\Administrative Tools`.
4. Open `Computer Management` and select `Local Users and Groups` > `Groups`.
5. Open `Remote Desktop Users` and add the new user to the group.

# Removing Users
1. Navigate to `Control Panel\User Accounts\User Accounts\Manage Accounts`.
2. Select the user you want to delete and click `Delete the account`.
3. This should automatically delete them from the `Remote Desktop Users` group.

**Note** - You may be required to run the EC2 instance as a `dedicated instance` to fully adhere with Microsoft licensing agreements. This only applies if your CALs do not include `license mobility` for multi-tenant environments.
