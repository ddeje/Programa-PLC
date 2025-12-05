# Configurar SSH para Acceso Remoto al Jetson

## 🎯 OBJETIVO
Permitir que desde tu PC puedas conectarte al Jetson sin contraseña,
para que yo (Copilot) pueda ejecutar comandos directamente.

---

## PASO 1: Copiar tu clave SSH al Jetson

### Opción A: Desde el Jetson (si tienes acceso físico)

1. Conecta teclado y monitor al Jetson
2. Abre una terminal
3. Ejecuta estos comandos:

```bash
# Crear directorio .ssh si no existe
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Agregar tu clave pública
echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDjnQKPWd8//oYp1ax6hQmB7CMeorK5v5GsJTTvsAcLyZYHKF9A4dbccgtIgz2zF3YCNcTNPmH5YtBHU0umdrkHgSWbmKMy+w/ROi2VDregIOOj31bHk8Oys56lvUlkS9y/nOCj07TmaxDaR3gaaQZcMMk/GCccC6iFfvPHyb7xpNicJUCa5U024WLkRE3jQleq+N7+uHT31mHqQZoxbcT1IWhIHGp+MyyWoA8AUls+Sx7jD8WemMm032tCitSIVPUvcakdXJJEdQ05/47Y40/YpGc2a6R5y0qikZoB5W9QrQGiDVP/HYceO8q6IOfNx2okrODIvj1gmsoJVJmLV0WQa/CY+H8d8fgmsdCC3j66/QuIVU6CAmx0K7fCrqJwu25xSt4GE245T/MIA73Kyl3yPQJQgAgNePwZIWtJCWMYE1zYZ87SKgzQWLJkFzpVXndhNFXWW00qva2AavYW/IBq+aFWxhrcv8WW7ikUeZgTbLdNsReHCOMLGX739zbYIEbhnhJHsZCnFJRFCuJF6f+uFCf71wOWhQ0hJRsSQmso1MRvT5t8O6Ks9kCIEQeGsdn+9Z9cyvPJsGBukZovylwkC7RYmTIHy93/G5wduUvkFnhecb3YLxLRJhGBCSpJOyO9RiSkrb+XSKIECgsrpqy/PcIrIUu1JwtbQy0N15HZGQ== 18035@Lei' >> ~/.ssh/authorized_keys

# Establecer permisos correctos
chmod 600 ~/.ssh/authorized_keys

# Verificar que se guardó
cat ~/.ssh/authorized_keys
```

### Opción B: Si conoces la contraseña del Jetson

Desde tu PC Windows (PowerShell):
```powershell
# Reemplaza PASSWORD con la contraseña real
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh mlc-710aix@192.168.101.110 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

---

## PASO 2: Probar la conexión

Desde tu PC:
```powershell
ssh mlc-710aix@192.168.101.110
```

Si funciona, deberías conectarte **SIN que pida contraseña**.

---

## PASO 3: Verificar que SSH funciona

Una vez conectado, verifica:
```bash
# Ver hostname
hostname

# Ver contenedores Docker
docker ps

# Ver logs del contenedor OPC UA
docker logs almaco_apl_opcua-almacoAplOpcua-1 --tail 20
```

---

## 🔧 TROUBLESHOOTING

### Error: "Permission denied (publickey)"
- La clave no se copió correctamente
- Verificar permisos: `ls -la ~/.ssh/`
- Los permisos deben ser: `drwx------` para .ssh y `-rw-------` para authorized_keys

### Error: "Connection refused"
- El servicio SSH no está corriendo
- En el Jetson: `sudo systemctl status ssh`
- Iniciar: `sudo systemctl start ssh`

### Error: "Host key verification failed"
- Eliminar la entrada vieja: 
```powershell
ssh-keygen -R 192.168.101.110
```

---

## ✅ VERIFICACIÓN FINAL

Una vez configurado, yo (Copilot) podré ejecutar comandos como:

```powershell
# Desde tu PC
ssh mlc-710aix@192.168.101.110 "docker logs almaco_apl_opcua-almacoAplOpcua-1 --tail 50"
```

Y ver los logs del Jetson directamente para hacer troubleshooting en tiempo real.

---

## 📞 ALTERNATIVA: Si no puedes configurar SSH

Si no es posible configurar SSH, podemos usar un script que tú ejecutes manualmente:

1. Yo genero los comandos que necesito
2. Tú los copias y ejecutas en el Jetson
3. Tú me pegas el resultado

Es más lento pero funciona igual.
