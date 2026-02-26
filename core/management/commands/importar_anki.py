import os
import zipfile
import sqlite3
import json
import re
import uuid
import tempfile
import shutil
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from core.models import Flashcard
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Importa flashcards e imagens de um arquivo .apkg para o sistema'

    def add_arguments(self, parser):
        parser.add_argument('caminho_apkg', type=str, help='Caminho para o arquivo .apkg')
        parser.add_argument('--user_id', type=int, help='ID do usuário proprietário (vazio para Público)')

    def handle(self, *args, **options):
        caminho_apkg = options['caminho_apkg']
        user_id = options.get('user_id')
        usuario = User.objects.filter(id=user_id).first() if user_id else None

        if not os.path.exists(caminho_apkg):
            self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {caminho_apkg}'))
            return

        tmp_dir = tempfile.mkdtemp()
        conn = None  # Inicializa para garantir que podemos fechar depois

        try:
            with zipfile.ZipFile(caminho_apkg, 'r') as z:
                z.extractall(tmp_dir)

                # 1. Mapear mídias
                media_map_path = os.path.join(tmp_dir, 'media')
                media_map = {}
                if os.path.exists(media_map_path):
                    with open(media_map_path, 'r', encoding='utf-8') as f:
                        media_map = json.load(f)

                inv_media_map = {v: k for k, v in media_map.items()}

                # 2. Localizar e conectar ao SQLite (Ajuste para compatibilidade)
                lista_arquivos = os.listdir(tmp_dir)
                db_arquivo = next((f for f in lista_arquivos if f.startswith('collection.anki')), None)

                if not db_arquivo:
                    self.stdout.write(self.style.ERROR("Banco de dados Anki não encontrado no arquivo."))
                    return

                db_path = os.path.join(tmp_dir, db_arquivo)
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # 3. Processar Notas
                cursor.execute("SELECT flds FROM notes")

                contador = 0
                for row in cursor.fetchall():
                    campos = row[0].split('\x1f')
                    pergunta = campos[0]
                    resposta = campos[1]

                    card = Flashcard(
                        usuario=usuario,
                        pergunta=pergunta,
                        resposta=resposta,
                        categoria="Importado do Anki",
                        is_publico=(usuario is None)
                    )

                    # 4. Lógica de Imagem com UUID
                    img_match = re.search(r'<img src="([^"]+)">', pergunta + resposta)

                    if img_match:
                        nome_original = img_match.group(1)
                        if nome_original in inv_media_map:
                            nome_no_zip = inv_media_map[nome_original]
                            caminho_img_extraida = os.path.join(tmp_dir, nome_no_zip)

                            if os.path.exists(caminho_img_extraida):
                                with open(caminho_img_extraida, 'rb') as img_f:
                                    # O Django renomeia para UUID aqui conforme o model
                                    card.imagem.save(
                                        nome_original,
                                        ContentFile(img_f.read()),
                                        save=False
                                    )

                    card.save()
                    contador += 1

                self.stdout.write(self.style.SUCCESS(f'Sucesso! {contador} cards importados.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro na importação: {e}'))
        finally:
            # CORREÇÃO: Fechar a conexão explicitamente antes de deletar a pasta
            if conn:
                conn.close()

            # Pequeno delay ou verificação para garantir que o Windows liberou o arquivo
            try:
                shutil.rmtree(tmp_dir)
            except PermissionError:
                self.stdout.write(self.style.WARNING(
                    f"Aviso: Não foi possível limpar a pasta temporária {tmp_dir}. Você pode apagá-la manualmente depois."))