Scrapy Spider

Este proyecto es un web scraper construido con Scrapy que recopila letras de canciones desde el sitio web Letras.com, categorizándolas por género y detectando el idioma en que están escritas.

Características

Extrae letras de canciones de más de 80 géneros musicales.

Detecta el idioma de la letra utilizando langdetect.

Guarda los datos en formato JSONL.

Evita la duplicación de canciones mediante un hash único.

Requisitos

Asegúrate de tener instalado Python 3 y Scrapy. Puedes instalar las dependencias con:

pip install scrapy langdetect

Uso

Para ejecutar el spider y comenzar la recopilación de datos:

scrapy runspider Scrapy.py

Los datos recolectados se guardarán en final.jsonl.

Estructura del JSON de salida

Cada canción recolectada se guarda en final.jsonl con el siguiente formato:

{
  "id": "código_md5_unico",
  "genre": "nombre_del_género",
  "song_url": "url_de_la_canción",
  "title": "título_de_la_canción",
  "artist": "nombre_del_artista",
  "languages": ["es", "en"],
  "lyrics": "letra de la canción"
}

Personalización

Si deseas cambiar el número de canciones por género, edita la variable max_results_per_genre dentro del código, para temas de obtencion del 100% se usa 1000

Notas

Si una canción tiene varios fragmentos en distintos idiomas, el scraper intentará identificarlos con un nivel de confianza mayor al 90%.

Se ha implementado un filtro especial para detectar letras en japonés mediante caracteres kanji.

Si un ID de canción ya fue procesado, se marca como "DUPLICADOS".

