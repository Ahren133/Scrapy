import scrapy
import json
import hashlib
import langdetect
import re
from langdetect import detect_langs

class SongLyricsSpider(scrapy.Spider):
    name = "song_lyrics"  
    
    genres = [
        "afrobeats", "alternativo-indie", "rock-alternativo", "musica-andina", "arrocha", 
        "axe", "bachata", "musica-de-banda", "blues", "bolero", "bossa-nova", "funk", 
        "brega-funk", "brega", "classico", "corridos", "country", "cuarteto", "cumbia", 
        "dance", "dancehall", "dembow", "disco", "eletronica", "emocore", "experimental", 
        "fado", "flamenco-bulerias", "folk", "forro", "funk-internacional", "gospelreligioso", "gotico", 
        "grunge", "guarania", "hard-rock", "hardcore", "heavy-metal", "hip-hop-rap", "house", 
        "hyperpop", "industrial", "instrumental", "j-popj-rock", "jazz", "k-pop", "infantil", 
        "mpb", "mambo", "marchas-hinos", "mariachi", "merengue", "metal", "nativista", "new-age", 
        "new-wave", "velha-guarda", "pagode", "piseiro", "pop", "poprock", "post-rock", "power-pop", 
        "progressivo", "psicodelia", "punk-rock", "rb", "ranchera", "reggae", "reggaeton", "regional", 
        "rock", "rock-roll", "rockabilly", "romantico", "salsa", "samba", "samba-enredo", "sertanejo", 
        "ska", "soft-rock", "soul", "surf-music", "tango", "tecnopop", "trap", "trova", "turreo-rkt", 
        "vallenato", "world-music", "xote", "jovem-guarda", "zamba", "zouk"
    ]

    max_results_per_genre = 5
    seen_ids = set()  

    def start_requests(self):
        for genre in self.genres:
            url = f"https://www.letras.com/mais-acessadas/{genre}/"  
            yield scrapy.Request(url=url, callback=self.parse_genre, meta={'genre': genre, 'count': 0})  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        open("final.jsonl", "w", encoding="utf-8").close() 
    
    def parse_genre(self, response):
        genre = response.meta['genre']  
        count = response.meta['count']  
        
        songs = response.css("ol.top-list_mus li")   
        if not songs:
            self.logger.warning(f"No se encontraron canciones en el género {genre}.")  
            return 
        
        for song in songs:
            if count >= self.max_results_per_genre:  
                break
            
            song_url = song.css("a::attr(href)").get() 
            song_title = song.css("b.font::text").get()  
            artist_name = song.css("span.font::text").get()  
            
            if song_url and song_title and artist_name:
                full_url = "https://www.letras.com" + song_url  
                count += 1  
                yield scrapy.Request(url=full_url, callback=self.parse_lyrics, meta={'title': song_title.strip(), 'artist': artist_name.strip(), 'genre': genre})  
        
        if count < self.max_results_per_genre:
            next_page = response.css("a.next::attr(href)").get()  
            if next_page:
                next_page_url = "https://www.letras.com" + next_page  
                yield scrapy.Request(url=next_page_url, callback=self.parse_genre, meta={'genre': genre, 'count': count})  

    def parse_lyrics(self, response):
        title = response.meta['title']  
        artist = response.meta['artist'] 
        genre = response.meta.get('genre', 'unknown')  
        
        lyrics = response.css("div.lyric p::text, div.lyric-original p::text").getall()  
        
        if not lyrics:
            lyrics = response.css("div.lyric-original p span.verse span::text").getall()  
        
        if lyrics:
            lyrics = " ".join([line.strip() for line in lyrics if line.strip()])  
        
        # Detectar idiomas de los fragmentos de la letra con mejoras
        languages = set()  
        MIN_LENGTH = 80  # Longitud mínima para evitar falsos positivos
        fragments = re.split(r'(?<=\.|\?)\s+', lyrics)  # Divide la letra en fragmentos
        
        for fragment in fragments:
            if len(fragment) >= MIN_LENGTH:  # Filtra fragmentos cortos
                try:
                    detected_languages = detect_langs(fragment)  # Detecta varios idiomas con probabilidades
                    for lang in detected_languages:
                        if lang.prob > 0.90:  # Solo agrega idiomas con confianza >70%
                            languages.add(lang.lang)
                except langdetect.lang_detect_exception.LangDetectException:
                    pass  
        
        # Detectar japonés (kanji)
        if re.search(r'[\u4e00-\u9fff]+', lyrics):  # Si contiene caracteres kanji
            languages.add('ja')  
        
        languages = list(languages) 
        
        unique_id = hashlib.md5(f"{title}{artist}".encode('utf-8')).hexdigest()
        
        if unique_id in self.seen_ids:
            unique_id = "DUPLICADOS"  
        else:
            self.seen_ids.add(unique_id)  
        
        song_data = {
            "id": unique_id,
            "genre": genre,
            "song_url": response.url,
            "title": title,
            "artist": artist,
            "languages": languages,
            "lyrics": lyrics
        }
        
        with open("final.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(song_data, ensure_ascii=False) + "\n")  
        
        yield song_data

