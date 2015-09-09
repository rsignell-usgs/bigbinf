Docker registry 2 requires TLS when serving non localhost. 
To run docker registry with TLS you must pass the certificate and key.
```sh
docker run -d -p 5000:5000 --restart=always --name registry \
  -v `pwd`/certs:/certs \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
  registry:2
```

To create a certificate:
```sh
openssl req \
  -newkey rsa:4096 -nodes -sha256 -keyout certs/registry.key \
  -x509 -days 365 -out certs/registry.crt
 ```

 However just doing this results in errors when using docker CLI to perform operations on the remote registry. Docker doesn't accept the certificate even after adding it to `/etc/docker/certs.d/<IP:port>/ca.crt`.

 The solution comes from here: [https://github.com/docker/distribution/issues/948]

 Before creating the certificate you must add the domain/IP of the docker registry to ` /etc/ssl/openssl.cnf`. Example:
```sh
...
[ v3_ca ]
subjectAltName = IP:192.168.1.102
...
```
After this you can create the certificate on the machine that you performed the above. You can now continue to add the certificate to the docker directory. docker should now accept the certificate as valid.