import csv
import os
from django.core.management.base import BaseCommand
from explore_gunung.models import Gunung

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE_DIR, 'MastersheetsGunung-Sheet1.csv')

class Command(BaseCommand):
    help = 'Mengimpor data Gunung dari file Mastersheets Gunung - Sheet1.csv'

    def handle(self, *args, **options):
        # 1. Pastikan tabel model Gunung sudah ada
        if not Gunung._meta.db_table:
            self.stdout.write(self.style.ERROR('Tabel Gunung belum ada. Jalankan: python manage.py migrate'))
            return

        # 2. Buka file CSV
        try:
            with open(CSV_PATH, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                gunung_list = []
                for row in reader:
                    # 3. Mapping data CSV ke field model Django
                    gunung_list.append(
                        Gunung(
                            nama=row['Nama Gunung'],
                            ketinggian=row['Tinggi (mdpl)'], # Otomatis dikonversi ke Integer
                            provinsi=row['Provinsi Gunung'],
                            deksripsi=row['Deskripsi'],
                            foto=row['Foto (url)'] if row['Foto (url)'] != 'nan' else '', # Menangani nilai 'nan' pada kolom url
                        )
                    )
                
                # 4. Melakukan bulk creation (memasukkan semua data sekaligus)
                Gunung.objects.bulk_create(gunung_list)
                
                self.stdout.write(self.style.SUCCESS(f'Berhasil mengimpor {len(gunung_list)} data Gunung.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File tidak ditemukan: {CSV_PATH}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Terjadi kesalahan: {e}'))