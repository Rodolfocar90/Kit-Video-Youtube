# config/

Aquí se guarda `models.json`: la lista de modelos de Gemini que tiene tu
cuenta y cuál usa el kit para cada tarea (texto, vídeo, imagen).

**No contiene ningún secreto**, así que puedes versionarlo sin problema.

Se genera solo la primera vez que se usa el kit. Para regenerarlo:

```bash
python3 scripts/models.py --refresh
```

Bórralo si cambias de cuenta de Google o si Google retira un modelo y
quieres que el kit vuelva a elegir.
