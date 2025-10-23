import csv
import os
from django.core.management.base import BaseCommand
from artikel.models import Artikel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, 'artikelgunung-Sheet1.csv')

class Command(BaseCommand):
    help = 'Mengimpor data Artikel dari CSV (otomatis deteksi delimiter)'

    def handle(self, *args, **options):
        try:
            with open(CSV_PATH, mode='r', encoding='latin-1', newline='') as file:
                content = file.read()
                file.seek(0)

                # 🔹 Tes delimiter secara manual
                if '\t' in content:
                    delimiter = '\t'
                elif ';' in content:
                    delimiter = ';'
                else:
                    delimiter = ','

                reader = csv.DictReader(file, delimiter=delimiter)

                # Debug lihat header
                headers = reader.fieldnames
                print("DEBUG HEADER KEYS:", headers)

                artikel_list = []
                for row in reader:
                    keys = {k.strip().lower(): (v or '').strip() for k, v in row.items()}
                    artikel_list.append(
                        Artikel.objects.create(
                            title=keys.get('judul', ''),
                            description=keys.get('isi', ''),
                            image=keys.get('thumbnail', ''),
                        )
                    )

                Artikel.objects.bulk_create(artikel_list)
                self.stdout.write(self.style.SUCCESS(f'✅ Berhasil mengimpor {len(artikel_list)} data Artikel.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File tidak ditemukan: {CSV_PATH}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Terjadi kesalahan: {e}'))
