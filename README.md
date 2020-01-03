# serverless-aws-ddns

Created a simple, AWS based, DDNS service that I use with my Synology DS1618+ ...

## Configure

Create a file called `config.<STAGE>.yml`. Contents should look something like this:

```
---
deployment_bucket: whatever-${self:provider.stage}-serverless-deployments
log_level: INFO

secret_key: <YOUR_SECRET_KEY>

route_53:
  zone_id: Z63XFG2QFVA8D
  zone_name: example.com

custom_domain: ddns.example.com
certificate_name: ddns.example.com
```

~ replace values where needed!

## Token Based Authentication

As mentioned in the 'Configure' section, I added token based authentication to the API. This requires a 'secret' (~ configured in `config.<STAGE>.yml`) and a valid token.

### Dependencies

I used (`cryptography`)[https://pypi.org/project/cryptography/]. Create a `venv` and run `pip3 install -r requirements.txt`.

### Generate Secret
> Only once per environment/stage.

```
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key)
```

Now, store `key` in `config.<STAGE>.yml`.

### Generate Token
> Generate for each client.

```
$ ./generate_token.sh --env <ENV> --hostname <HOSTNAME>
```

Example:

```
$ ./generate_token.sh --env dev --hostname foobar

INFO:ddns:Here's your token for hostname 'foobar':

gAAAAABeD0lSrrYujA7ffPmPLe3IskEsJIIDiS7d0VqB8kccG0-ZPYiU-p9sD5JwJiRvska09rZpUGMwa_5Duwr54b6phTfqVg==
```

The generated token can be used in your client (for example your Synology). Use as value for `token` queryString parameter.

## Deploy
> The simple version ;)

```
$ npm i
$ sls deploy
```

## Create custom domain

```
$ sls create_domain
```

## Configure Synology

### Add new Service Provider
> `Control Panel -> External Access`

* Press `Customize`
* `Service provider`: `<WHATEVER>`
* `Query URL`: `https://URL?hostname=__HOSTNAME__&myip=__IP__&token=__PASSWORD__`

Press `Save`

### Configure DDNS
> `Control Panel -> External Access`

* Press `Add`
* Select `Service Provider`
* `Hostname`: `<HOSTNAME>`
* `Username`: `<EMPTY>`
* `Password/Key`: `<TOKEN>`

Where:
* `<HOSTNAME>` is a **hostname** ... not a URL!
* `<TOKEN>` is the result of running the `generate_token.sh` bash script.

Press `Test Connection` to check if all is ok ...

If the `<TOKEN>` is invalid, you'll get an `Unauthorized` ... just saying.

~ the end