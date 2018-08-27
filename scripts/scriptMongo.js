
        use mfaprovider
        db.createUser(
            {
                user:"admin",
                pwd:"admin",
                roles: ["readWrite","dbAdmin"]
            }
        )
        