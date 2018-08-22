use mfaprovider
db.createUser(
    {
        user:"admin3",
        pwd:"admin",
        roles: ["readWrite","dbAdmin"]
    }
)
