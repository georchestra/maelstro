# Installation with geOrchestra

Configuration of the [datadir](https://github.com/georchestra/datadir) of geOrchestra

## Security proxy integration
in the `security-proxy/targets-mapping.properties` file, add : 
```
maelstro-backend=http://${MAELSTRO_HOST}:8000/
maelstro=http://${MAELSTRO_FRONT_HOST}:8080/maelstro/
```
You will need to customize the env var linked with the good host.

in `security-proxy/security-mappings.xml` file, add the following access rules :
```
   <intercept-url pattern="/maelstro-backend.*" access="ROLE_MAELSTRO" />
   <intercept-url pattern="/maelstro.*" access="ROLE_MAELSTRO" />
```

## Gateway configuration
In the `gateway/routes.yaml` file, edit the `spring.cloud.gateway.routes` section to add the following:
```
       - id: maelstro-back
         uri: ${georchestra.gateway.services.maelstro-back.target}
         predicates:
         - Path=/maelstro-backend/**
         filters:
         - RewritePath=/maelstro-backend/(?<segment>.*),/$\{segment}
       - id: maelstro
         uri: ${georchestra.gateway.services.maelstro.target}
         predicates:
         - Path=/maelstro/**
         filters:
         - RewritePath=/maelstro/(?<segment>.*),/$\{segment}
```
Them, `gateway/gateway.yaml` file, edit the `georchestra.gateway.services` section :
```
       maelstro-back:
         target: ${georchestra.gateway.services.maelstro-back.target}
         access-rules:
           - intercept-url: /maelstro-backend/**
             anonymous: false
             allowed-roles: MAELSTRO
       maelstro:
         target: ${georchestra.gateway.services.maelstro.target}
         access-rules:
           - intercept-url: /maelstro/**
             anonymous: false
             allowed-roles: MAELSTRO
```
In the same file, add the following into the `georchestra.gateway.services` section:
```
  maelstro-back.target: http://${MAELSTRO_HOST}:8000/
  maelstro.target: http://${MAELSTRO_FRONT_HOST}:8080/
```

## Geoserver

Maelstro assumes that the destination workspace and datastore exist, otherwise it will return an error.

Before using it, make sure that the source and destination geoservers are aligned.

## Console

To access the Maelstro module without being a super administrator, the MAELSTRO role is required.

You should also double check the credentials which are used to perform the API calls on the source and destination platforms in the [config.yaml](config.yaml) file.

## Header integration 

[TODO]
