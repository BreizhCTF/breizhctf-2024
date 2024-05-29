# NginFail

## Solve

Dans ce challenge, après avoir téléchargé les sources, on remarque la configuration nginx suivante :

```
server {
    listen       80;
    listen  [::]:80;
    server_name  localhost;

    root /;

    location /index.html {
	add_header Content-Type text/html;
	return 200 '<html><head><title>Hello world</title></head><body>Hello World, from Nginx !</body></html>';
    }

    error_page 403 =302 /index.html;
}

```

Dans cette configuration, on remarque la directive suivante: *root /*

Cette directive indique à nginx que le root du filesystem est */*, on a donc accès à tous le filesystem depuis le site web.

Il faut donc taper sur `https://nginfail.ctf.bzh/opt/flag/flag.txt`.

## Flag

BZHCTF{b3_c4r3ful_w1th_r00t_d1r3ct1v3}