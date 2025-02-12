{{- define "maelstro.bootstrap_maelstro_configuration" -}}
- name: bootstrap-maelstro-configuration
  image: bitnami/git
  command:
  - /bin/sh
  - -c
  - {{- if .Values.datadir.git.ssh_secret }}
    mkdir -p /root/.ssh ;
    cp /ssh-secret/ssh-privatekey /root/.ssh/id_rsa ;
    chmod 0600 /root/.ssh/id_rsa ;
    {{- end }}
    rm -Rf /etc/georchestra ;
    git clone --depth 1 --single-branch {{ .Values.datadir.git.url }} -b {{ .Values.datadir.git.ref }} /etc/georchestra ;
  {{- if .Values.datadir.git.ssh_secret }}
  env:
    - name: GIT_SSH_COMMAND
      value: ssh -o "IdentitiesOnly=yes" -o "StrictHostKeyChecking no"
  {{- end }}
  volumeMounts:
  - mountPath: /etc/georchestra
    name: georchestra-datadir
  {{- if .Values.datadir.git.ssh_secret }}
  - mountPath: /ssh-secret
    name: ssh-secret
  {{- end }}
{{- end -}}
