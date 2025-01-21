# Maelstro docker composition

accessible from https://georchestra-127-0-0-1.nip.io/maelstrob/



Start composition

```
git submodule update --init --recursive
cd config
git apply ../0001-tweat-gateway-and-security-proxy-config-to-host-mael.patch
cd ..
docker compose up -d
```

