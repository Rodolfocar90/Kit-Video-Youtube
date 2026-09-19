"""Librería interna del Kit de Vídeo para YouTube.

Reglas de este paquete:
  * Los secretos se leen SOLO de variables de entorno / .env
  * Ninguna función imprime una clave completa (usa mask())
  * Toda acción con coste pasa por guard.confirm_cost()
"""
