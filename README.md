# serverless-aws-ddns

Created a simple, AWS based, DDNS service that I use with my Synology DS1618+ ...

## Configure

Create a file called `config.<STAGE>.yml`. Contents should look something like this:

```
---
route_53:
  zone_id: Z63XFG2QFVA8D

custom_domain: ddns.example.com
certificate_name: ddns.example.com
```

~ replace values where needed!

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

> `Control Panel -> External Access -> Customize`


* `Service provider`: `<WHATEVER>`
* `Query URL`: `https://URL?hostname=__HOSTNAME__&myip=__IP__&token=__PASSWORD__`

Press `Save`

### Configure DDNS

* Press `Add`
* Select `Service Provider`
* `Hostname`: `<HOSTNAME>` (~ valid `fqdn`)
* `Username`: `<EMPTY>`
* `Password/Key`: `<TOKEN>`


Press `Test Connection` to check if all is ok ...

~ the end