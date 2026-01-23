#!/usr/bin/env python3
"""
Script de mantenimiento: normaliza los usuarios en la BD:
- añade ".com" al dominio de los emails que no lo tengan
- establece la contraseña a 'Limpiez123.' (hash bcrypt)

El script hace una copia de seguridad de la base de datos antes de modificarla.
Usarlo con precaución.
"""

import shutil
import os
import bcrypt
from core.base_datos.ConfiguracionBD import RUTA_BD, OBTENER_SESION, MODELO_USUARIO


def normalizar_email(email: str) -> str:
    if not email:
        return email
    email = email.strip()
    if email.endswith('.com'):
        return email
    if '@' in email:
        local, domain = email.split('@', 1)
        if domain.endswith('.com'):
            return email
        return f"{local}@{domain}.com"
    return email + '.com'


def main():
    # respaldo
    if os.path.exists(RUTA_BD):
        respaldo = RUTA_BD + '.backup'
        shutil.copy2(RUTA_BD, respaldo)
        print(f"Respaldo creado: {respaldo}")
    else:
        print(f"No existe la BD en {RUTA_BD}")

    sesion = OBTENER_SESION()
    usuarios = sesion.query(MODELO_USUARIO).all()
    if not usuarios:
        print("No se encontraron usuarios.")
        return

    new_pw = 'Limpiez123.'
    salt = bcrypt.gensalt(rounds=12)
    new_hash = bcrypt.hashpw(new_pw.encode('utf-8'), salt).decode('utf-8')

    modificados = 0
    for u in usuarios:
        original_email = u.EMAIL or ''
        nuevo_email = normalizar_email(original_email)
        cambio = False
        if nuevo_email != original_email:
            u.EMAIL = nuevo_email
            cambio = True

        # actualizar contraseña de referencia
        u.CONTRASENA_HASH = new_hash
        cambio = True

        if cambio:
            modificados += 1
            sesion.add(u)

    sesion.commit()
    print(f"Usuarios procesados: {len(usuarios)}. Usuarios modificados: {modificados}.")
    print("Contraseñas actualizadas a 'Limpiez123.' (hash bcrypt). Revise el respaldo si quiere revertir.")


if __name__ == '__main__':
    main()
