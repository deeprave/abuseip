# abuseip

This is a utility that makes use of the API from abuseipdb.com, which
tracks reports of remote abuse on public facing internet systems.

The idea here is to create a useful list of remote addresses to ban,
similar to [fail2ban](https://www.fail2ban.org/), but much simplified
and designed for a specific use case.

## Purpose
The aims of this utility are:
- generate a deny list for including into nginx
- check on specific IP to determine reputation
- (not yet implemented) report a specific IP for abuse

## Requirements
To use this utility, you need to have an api key from abuseipdb.com.

After creating you account, head to your account details and select
the APIv2 tab where you can create an API key.

This key must be placed into a file with the name ".apikey" and
stored along with the script, or in the directory form which the
utility is run. Format of this file is as follows:
```
APIKEY=<your_api_key>
```

While creating an account is free of charge, data limits are very
severe and make the functionality of a free account not particularly
useful for generating blacklists.
