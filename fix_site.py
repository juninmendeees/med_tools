import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django1.settings')
django.setup()

from django.contrib.sites.models import Site


def fix():
    # 1. Deletamos qualquer site que use o nosso domínio para evitar o erro de duplicidade
    Site.objects.filter(domain='127.0.0.1:8000').delete()

    # 2. Deletamos o ID 1 caso ele esteja ocupado por outro nome (como example.com)
    Site.objects.filter(id=1).delete()

    # 3. Criamos o registro limpo com o ID exigido pelo seu settings.py
    site = Site.objects.create(
        id=1,
        domain='127.0.0.1:8000',
        name='MedTools Local'
    )

    print(f"Sucesso! Site configurado: {site.domain} com ID: {site.id}")


if __name__ == "__main__":
    fix()